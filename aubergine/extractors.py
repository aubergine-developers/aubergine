"""Extractors for various parts of the request."""
import abc
from enum import Enum
from aubergine.common import Loggable
from aubergine.decoders import PlainDecoder, JSONDecoder


class Location(Enum):
    """Possible location parameters."""
    QUERY = 'query'
    HEADER = 'header'
    PATH = 'path'
    COOKIE = 'cookie'


class ParameterMissingError(ValueError):
    """An error raised when some parameter value was not present in request."""

    def __init__(self, location, name):
        super(ParameterMissingError, self).__init__(location, name)
        self.location = location
        self.name = name


class ParameterValidationError(ValueError):
    """An error raised when some parameter value failed to validate."""

    def __init__(self, validation_errors):
        super(ParameterValidationError, self).__init__(validation_errors)
        self.errors = validation_errors


class Extractor(abc.ABC):
    """Base class for extracting content from HTTP requests."""

    def __init__(self, schema, decoder):
        self.schema = schema
        self.decoder = decoder

    @abc.abstractmethod
    def read_data(self, req, **kwargs):
        """Read data from te request and path arguments.

        The concrete implementations of this class should only read data from specific part
        of request and return raw str or bytes. Decoding of the read data is done in
        :py:meth:`Extractor.extract` method.

        :param req: HTTP request
        :type req: :py:class:`falcon.Request`
        :param kwargs: keyword arguments with path parameters.
        """
        pass

    def extract(self, req, **kwargs):
        """Extract data from the request.

        :param req: HTTP request
        :type req: :py:class:`falcon.Request`
        :param kwargs: keyword arguments with path parameters.
        :returns: content read from the Extractor-specific part of the request
        :rtype: str or bytes
        """
        data = self.read_data(req, **kwargs)
        decoded = self.decoder.decode(data)
        result = self.schema.load({'content': decoded})
        return result.data['content']


class BodyExtractor(Extractor):
    """Extractor for request's body."""

    @staticmethod
    def read_data(req, **kwargs):
        """Read data from HTTP request's body.

        :param req: http request.
        :type req: falcon.Request
        :param _kwargs: not used, provided for compliance with Extractor base class.
        :returns: content read from the request's body.
        :rtype: str or bytes
        """
        return req.bounded_stream.read()


class HeaderExtractor(Extractor):
    """Extractor for request's headers."""

    def __init__(self, schema, decoder, param_name, required):
        super(HeaderExtractor, self).__init__(schema, decoder)
        self.param_name = param_name
        self.required = required

    def read_data(self, req, **kwargs):
        """Read data from HTTP request's headers.

        :param req: http request.
        :type req: falcon.Request
        :param _kwargs: not used, provided for compliance with Extractor base class.
        :returns: content read from the request's header `self.param_name`.
        :rtype: str or bytes"""
        return req.get_header(self.param_name)


class QueryExtractor(Extractor):
    """Extractor for request's query parameters."""

    def __init__(self, schema, decoder, param_name, required):
        super(QueryExtractor, self).__init__(schema, decoder)
        self.required = required
        self.param_name = param_name

    def read_data(self, req, **kwargs):
        """Read data from HTTP request's query parameters.

        :param req: http request.
        :type req: falcon.Request
        :param _kwargs: not used, provided for compliance with Extractor base class.
        :returns: content read from the request's query param with this extractor's
         param_name.
        :rtype: str or bytes"""
        return req.get_param(self.param_name)


class PathExtractor(Extractor):
    """Extractor for request's path parameters.

    This extractors differs a lot from other extractors in that it uses provided kwargs
    rather than request. The kwargs for use with this handler should be the ones
    passed by falcon to the resource using this extractor.

    Note that another difference is that there are no optional path parameters.
    """

    def __init__(self, schema, decoder, param_name):
        super(PathExtractor, self).__init__(schema, decoder)
        self.param_name = param_name

    def read_data(self, req, **kwargs):
        """Read data from variable path component.

        :param req: http request, provided only for compliance with base class.
        :type req: falcon.Request
        :param _kwargs: dictionary of variable path parameters passed by falcon to the
         Resource, for which self is being used.
        :returns: value of kewyord argument with the same key as `param_name`.
        :rtype: str or bytes
        """
        if self.param_name not in kwargs:
            raise ParameterMissingError(Location.PATH, self.param_name)
        return kwargs[self.param_name]


class UnsupportedContentTypeError(ValueError):
    """Exception raised when we encounter content type not corresponding to any known decoder."""


class ExtractorBuilder(Loggable):
    """Class for building Extractors."""

    def __init__(self, schema_builder):
        self.schema_builder = schema_builder

    CONTENT_DECODER_MAP = {'application/json': JSONDecoder}

    def build_param_extractor(self, param_spec):
        """Build extractor for parameter described by given mapping.

        :param param_spec: parameter description in the form of mapping. Should conform to
         OpenAPI 3 specification but is not validated - this method is happy as long as it
         encounters any keys it needs.
        :type param_spec: mapping
        :returns: Extractor that can be used to extract parameters value from the request.
        :rtype: `Extractor`
        """
        location = param_spec['in']

        kwargs = {'param_name': param_spec['name']}

        if location == 'path':
            extractor_cls = PathExtractor
        elif location == 'query':
            extractor_cls = QueryExtractor
        elif location == 'header':
            extractor_cls = HeaderExtractor

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
        if extractor_cls != PathExtractor:
            kwargs['required'] = param_spec.get('required', False)
        return extractor_cls(**kwargs)

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
        schema = self.schema_builder.build(body_spec['content'][content_type]['schema'])
        return BodyExtractor(schema=schema, decoder=decoder)
