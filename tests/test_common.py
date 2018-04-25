"""Test cases for classes in common module."""
import pytest
from aubergine import common

@pytest.fixture(scope='session', name='loggable')
def loggable_derivative():
    """Fixture providing an implementation of Loggable abstract class."""

    class LoggableDerivative(common.Loggable):
        """Example subclass of Loggable."""
        def __init__(self, logger_name):
            self._logger_name = logger_name

        @property
        def logger_name(self):
            """Name of the logger."""
            return self._logger_name
    return LoggableDerivative

def test_loggable_calls_get_logger(mocker):
    """Loggable.logger property should use logging.getLogger to obtain a nnlogger instance."""
    get_logger_method = mocker.patch('aubergine.common.logging.getLogger')
    loggable = common.Loggable()
    logger = loggable.logger
    get_logger_method.assert_called_once_with(loggable.logger_name)
    assert logger == get_logger_method.return_value

@pytest.mark.parametrize('logger_name',
                         ['some-logger-name', 'some-other-logger-name'])
def test_names_logger_accordingly(mocker, logger_name, loggable):
    """Loggable.logger property should use logger_name property in getLogger calls."""
    get_logger_method = mocker.patch('aubergine.common.logging.getLogger')
    loggable = loggable(logger_name)
    logger = loggable.logger
    assert logger == get_logger_method.return_value
    get_logger_method.assert_called_once_with(logger_name)
