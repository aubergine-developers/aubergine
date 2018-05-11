"""Test cases for resource module."""
import pytest
from aubergine.resource import Resource

HTTP_METHODS = ('POST', 'GET', 'PUT', 'PATCH', 'OPTIONS', 'HEAD', 'DELETE')

@pytest.mark.parametrize('method', HTTP_METHODS)
def test_not_defined_methods(method, mocker):
    handlers = {other_method: mocker.Mock() for other_method in HTTP_METHODS
                if other_method != method}
    res = Resource(handlers, 'some/path/')
    with pytest.raises(AttributeError):
        getattr(res, 'on_' + method.lower())(mocker.Mock(), mocker.Mock())

def test_dispatch_to_handler(mocker):
    """Request's responders should forward requests to correct handlers."""
    handlers = {method: mocker.Mock() for method in HTTP_METHODS}
    resp = mocker.Mock()
    req = mocker.Mock()
    kwargs = {'arg1': 12, 'arg2': 'someargument'}
    resource = Resource(handlers, '/some/path/')
    for method in HTTP_METHODS:
        getattr(resource, 'on_' + method.lower())(req, resp, **kwargs)
        handlers[method].handle_request.assert_called_once_with(req, resp, **kwargs)
