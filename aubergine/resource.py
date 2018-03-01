"""Resource class."""
from functools import partial
import logging


class Resource(object):
    """Class for representing a HTTP resource."""

    def __init__(self, handlers, path):
        self.path = path
        self.handlers = {method.lower(): handler for method, handler in handlers.items()}
        self._construct_responders()

    def dispatch(self, method, req, resp, **kwargs):
        """Dispatch request to handler responsible for serving it."""
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
