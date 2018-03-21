"""Request handlers."""
import json
import falcon
from aubergine.decoders import ParameterValidationError


class RequestHandler(object):
    """Request handler.

    :param operation: a callable implementing the behaviour.
    :type operation: callable
    :param body_decoder: a decoder for for request body.
    :param params_decoders: a mapping of parameter names to respective decoders.
    """
    def __init__(self, operation, body_decoder, params_decoders):
        self.operation = operation
        self.body_decoder = body_decoder
        self.params_decoders = params_decoders

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

        if self.body_decoder is not None:
            op_kws['body'] = self.body_decoder.decode(req)

        resp.body = json.dumps(self.operation(**op_kws))

    def get_parameter_dict(self, req, **kwargs):
        """Create a dictionary of parameters from request and (possibly) path parameters.

        :param req: request object.
        :type req: :py:class:`falcon.Request`
        :param kwargs: placeholder for possibly present path parameters.
        :returns: a mapping of parameter names into the decoded values.
        :rtype: dict
        """
        try:
            return {name: dec.decode(req, **kwargs) for name, dec in self.params_decoders.items()}
        except ParameterValidationError as exc:
            raise falcon.HTTPBadRequest(*exc.errors)
