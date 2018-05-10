"""Implementation of Resource suitable for use with the Falcon Framework."""
from functools import partial
import logging


class Resource(object):
    """Class for representing a HTTP resource.

    The instances of this class implement :py:mod:`falcon` compatible Resource interface
    but are created dynamically from given mapping of request handlers.

    :param handlers: a maping of http method to some objects able to handler http reuqest
     via their handle_request method.
    :type:handlers: dict
    :param path: a path of the url at which this Resource will be used..
    :type path: str
    """
    def __init__(self, handlers, path):
        self.path = path
        self.handlers = {method.lower(): handler for method, handler in handlers.items()}
        self._construct_responders()

    def dispatch(self, method, req, resp, **kwargs):
        """Dispatch request to handler responsible for serving it.

        :param method: a http method as defined in HTTP standard (case insensitive).
        :type method: str
        :param req: a request just like the one passed to :py:mod:`falcon` responders.
        :param resp: a response object just like the one passed to Falcon responders
        :kwargs: keyword arguments - this will typically include path parameters passed Falcon.
        :return: the returned value of the correct handler for the given method. The content
         of the return value depends (obviously) only on the handler itself.
         The correct handler for the request is determined by method parameter.
        """
        self.logger.debug('Dispatching %s request to respective handler.', method)
        return self.handlers[method].handle_request(req, resp, **kwargs)

    @property
    def logger(self):
        """Logger used by this Resource."""
        return logging.getLogger('Resource: ' + self.path)

    def _construct_responders(self):
        for method in self.handlers:
            responder = partial(self.dispatch, method.lower())
            setattr(self, 'on_' + method.lower(), responder)


class ResourceBuilder:
    """Class for building Resource objects."""


    def __init__(self, extractor_builder):
        self.extractor_builder = extractor_builder

    def build_handler(self, handler_spec):
        pass
