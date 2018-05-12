"""Test cases for factories.py  modules."""
import pytest
from aubergine.factories import create_resource

HTTP_METHODS = ('POST', 'GET', 'PUT', 'PATCH', 'OPTIONS', 'HEAD', 'DELETE')

@pytest.mark.parametrize('other_method', HTTP_METHODS)
def test_creates_methods(other_method, mocker):
    handlers = {meth: mocker.Mock() for meth in HTTP_METHODS if meth != other_method}
    resource = create_resource(handlers)
    assert all(hasattr(resource, 'on_' + meth.lower()) for meth in handlers)
    assert not hasattr(resource, 'on_' + other_method.lower())

def test_dispatches_to_handlers(mocker):
    handlers = {meth: mocker.Mock() for meth in HTTP_METHODS}
    resource = create_resource(handlers)
    req = mocker.Mock()
    resp = mocker.Mock()
    kwargs = {'a': 10, 'b': 'xyz'}
    for meth in handlers:
        getattr(resource, 'on_' + meth.lower())(req, resp, **kwargs)
    for handler in handlers.values():
        handler.handle_request.assert_called_once_with(req, resp, **kwargs)
