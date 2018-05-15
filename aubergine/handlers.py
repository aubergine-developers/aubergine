"""Request handlers."""
import json
import falcon
from aubergine.extractors import ValidationError, MissingValueError


class RequestHandler:
    """Request handler.

    :param path: a path for which this handler is constructed
    :type path: str
    :param operation: a callable implementing the behaviour.
    :type operation: callable
    :param body_extractor: an extractor for request body.
    :param params_extractors: a collection of parameter extractors.
    """
    def __init__(self, path, operation, body_extractor, params_extractors):
        self.path = path
        self.operation = operation
        self.body_extractor = body_extractor
        self.params_extractors = params_extractors

    def handle_request(self, req, resp, **kwargs):
        """Process incoming request.

        :param req: request object.
        :type req: :py:class:`falcon.Request`
        :param resp: response being built.
        :type resp: :py:class:`falcon.Response`
        :param kwargs: placeholder for possibly present path parameters.
        :returns: None
        """
        op_kws = self.get_parameter_dict(req, **kwargs)

        if self.body_extractor is not None:
            op_kws['body'] = self.body_extractor.extract(req).value

        resp.body = json.dumps(self.operation(**op_kws))

    def get_parameter_dict(self, req, **kwargs):
        """Create a dictionary of parameters from request and (possibly) path parameters.

        :param req: request object.
        :type req: :py:class:`falcon.Request`
        :param kwargs: placeholder for possibly present path parameters.
        :returns: a mapping of parameter names into the extracted values.
        :rtype: dict
        """
        extracted = {}
        try:
            for name, extractor in self.params_extractors.items():
                present, value = extractor.extract(req, **kwargs)
                if present:
                    extracted[name] = value
            return extracted
        except ValidationError as exc:
            raise falcon.HTTPBadRequest(*exc.errors)
        except MissingValueError as exc:
            raise falcon.HTTPBadRequest({'error': 'parameter missing', 'name': exc.name,
                                         'location': exc.location})
