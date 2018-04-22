"""Common classes used in aubergine."""
import logging


class Loggable:
    """Base class for components supporting logging.

    This base class was extracted in case we switch to another logging framework at some
    point.
    """
    @property
    def logger_name(self):
        """Logger name of this loggable object."""
        return self.__class__.__name__

    @property
    def logger(self):
        """Get logger used by this class."""
        return logging.getLogger(self.logger_name)
