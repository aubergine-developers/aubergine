"""Extractors for various parts of the request."""
import abc


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
        return self.schema.load({'content': decoded})


class BodyExtractor(Extractor):
    """Extractor for request's body."""

    @staticmethod
    def read_data(req, **_kwargs):
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

    def read_data(self, req, **_kwargs):
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

    def read_data(self, req, **_kwargs):
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

    def read_data(self, _req, **kwargs):
        """Read data from variable path component.

        :param _req: http request, provided only for compliance with base class.
        :type req: falcon.Request
        :param _kwargs: dictionary of variable path parameters passed by falcon to the
         Resource, for which self is being used.
        :returns: value of kewyord argument with the same key as `param_name`.
        :rtype: str or bytes
        """
        return kwargs[self.param_name]