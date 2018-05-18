"""Extractors for various parts of the request."""
import collections
from enum import Enum
from functools import partial
from falcon import HTTPBadRequest
from aubergine.decoders import PlainDecoder, JSONDecoder


class Location(Enum):
    """Possible location parameters."""
    QUERY = 'query'
    HEADER = 'header'
    PATH = 'path'
    COOKIE = 'cookie'
    BODY = 'body'

ExtractionResult = collections.namedtuple('ExtractionResult', ['present', 'value'])


class MissingValueError(ValueError):
    """An error raised when some parameter value was not present in request."""

    def __init__(self, location, name=None):
        super(MissingValueError, self).__init__(location, name)
        self.location = location
        self.name = name


class ValidationError(ValueError):
    """An error raised when some parameter value failed to validate."""

    def __init__(self, validation_errors):
        super(ValidationError, self).__init__(validation_errors)
        self.errors = validation_errors


class Extractor: # pylint: disable=too-few-public-methods
    """Class for extracting parameter (or body) value from the request.

    :param schema: Schema for the parameter this extractor is for.
    :type schema: :py:class:`marshmallow.Schema`
    :param decoder: decoder for the raw data obtained from the request.
    :type decoder: object implementing `decode` method.
    :param required: whether corresponding parameter is required or not.
    :type required: bool
    :type read_data: callable for reading raw data from request. It should be possible
     to call it as read_data(request, **kwargs), where request is of the type
     :py:class:`falcon.Request`.
    """
    def __init__(self, schema, decoder, required, read_data):
        self.schema = schema
        self.decoder = decoder
        self.read_data = read_data
        self.required = required

    def extract(self, req, **kwargs):
        """Extract parameter from request and additional path arguments.

        :param req: request to extract value from
        :type req: :py:class:`falcon.Request`
        :param kwargs: keyword arguments - path parameters as passed by `falcon`.
        :returns: a tuple containing information wheather parameter was present
         in the request and, if so, its value.
        :rtype: :py:class:`ExtractionResult`
        :raises MissingValueError: if parameter was missing from request and the parameter
         is mandatory.
        :raises ValidationError: if parameter was present in the request but failed to validate
         against this extractor's schema.
        """
        try:
            raw = self.read_data(req, **kwargs)
        except MissingValueError as err:
            if self.required:
                raise err
            return ExtractionResult(present=False, value=None)
        decoded = self.decoder.decode(raw)
        data, errors = self.schema.load({'content': decoded})
        if errors:
            raise ValidationError(errors)
        return ExtractionResult(present=True, value=data['content'])

def read_body(req, **_):
    """Read raw data from request body.

    This function is designed to be passed as `read_data` to :py:class:`Extractor` initializer.
    """
    result = req.bounded_stream.read()
    if not result:
        raise MissingValueError(Location.BODY)
    return result

def read_header(req, param_name, **_):
    """Read parameter's raw data from request header.

    Partial of this function, with fixed `param_name` can be passed to :py:class:`Extractor`
    initializer.
    """
    try:
        return req.get_header(param_name, required=True)
    except HTTPBadRequest:
        raise MissingValueError(Location.HEADER, param_name)

def read_query(req, param_name, **_):
    """Read parameter's raw data from request query args.

    Partial of this function, with fixed `param_name` can be passed to :py:class:`Extractor`
    initializer.
    """
    try:
        return req.get_param(param_name, required=True)
    except HTTPBadRequest:
        raise MissingValueError(Location.QUERY, param_name)

def read_path(_req, param_name, **kwargs):
    """Read parameter's raw data from path parameters.

    Partial of this function, with fixed `param_name` can be passed to :py:class:`Extractor`
    initializer.
    """
    if param_name not in kwargs:
        raise MissingValueError(Location.PATH, param_name)
    return kwargs[param_name]


class UnsupportedContentTypeError(ValueError):
    """Exception raised when we encounter content type not corresponding to any known decoder."""


class ExtractorBuilder:
    """Class for building Extractors."""

    def __init__(self, schema_builder):
        self.schema_builder = schema_builder

    CONTENT_DECODER_MAP = {'application/json': JSONDecoder}

    READER_MAP = {'path': read_path, 'query': read_query, 'header': read_header}

    def build_param_extractor(self, param_spec):
        """Build extractor for parameter described by given mapping.

        :param param_spec: parameter description in the form of mapping. Should conform to
         OpenAPI 3 specification but is not validated - this method is happy as long as it
         encounters any keys it needs.
        :type param_spec: mapping
        :returns: Extractor that can be used to extract parameters value from the request.
        :rtype: `Extractor`
        """
        reader = partial(self.READER_MAP[param_spec['in']], param_name=param_spec['name'])
        kwargs = {}
        if 'content' in param_spec:
            content_type = next(iter(param_spec['content'].keys()))
            if content_type not in self.CONTENT_DECODER_MAP:
                raise UnsupportedContentTypeError(content_type)
            schema_spec = param_spec['content'][content_type]
            kwargs['decoder'] = self.CONTENT_DECODER_MAP[content_type]()
            kwargs['schema'] = self.schema_builder.build(schema_spec)
        else:
            kwargs['decoder'] = PlainDecoder()
            kwargs['schema'] = self.schema_builder.build(param_spec['schema'])
        kwargs['required'] = param_spec.get('required', False)
        return Extractor(read_data=reader, **kwargs)

    def build_body_extractor(self, body_spec):
        """Build extractor for body as described by given mapping.

        :param body_spec: body description in the form of mapping. Should conform to
         OpenAPI 3 specification but is not validated - this method is happy as long as it
         encounters any keys it needs.
        :type param_spec: mapping
        :returns: BodyExtractor that can be used to extract parameters value from the request.
        :rtype: `BodyExtractor`

        .. notes:: Currently this supports only a single content type. If multiple content types
           are given in the mapping the resulting body extractor will be constructed only for
           one of those.
        """
        content_type = next(iter(body_spec['content']))

        if content_type not in self.CONTENT_DECODER_MAP:
            raise UnsupportedContentTypeError(content_type)

        decoder = self.CONTENT_DECODER_MAP[content_type]()
        return Extractor(
            schema=self.schema_builder.build(body_spec['content'][content_type]['schema']),
            decoder=decoder,
            required=body_spec.get('required', False),
            read_data=read_body)
