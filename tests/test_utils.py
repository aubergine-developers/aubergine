"""Test cases for factories.py  modules."""
from functools import partial
import importlib
from nadia.api import SchemaBuilder
import pytest
from aubergine.extractors import ExtractorBuilder
from aubergine.operations import OperationLoader
from aubergine import utils
from aubergine.utils import create_resource

HTTP_METHODS = ('POST', 'GET', 'PUT', 'PATCH', 'OPTIONS', 'HEAD', 'DELETE')
OP_SPEC = {
    'operationId': 'my.module.operation',
    'requestBody': {'content': {'application/json': {'schema': {'type': 'string'}}}},
    'parameters': [
        {'name': 'name', 'in': 'path', 'schema': {'type': 'string'}},
        {'name': 'id', 'in': 'query', 'schema': {'type': 'integer'}}
    ]
}

BODYLESS_OP_SPEC = {key: value for key, value in OP_SPEC.items() if key != 'requestBody'}

@pytest.fixture(name='extractor_factory')
def _extractor_factory(mocker):
    """Fixture providing ExtractorBuilder mock."""
    return mocker.Mock(wraps=ExtractorBuilder(SchemaBuilder.create()))

@pytest.fixture(name='import_module')
def _import_module(mocker):
    """Fixture providing import_module mock."""
    return mocker.Mock(spec_set=importlib.import_module)

@pytest.fixture(name='create_handler')
def _create_handler(extractor_factory, import_module):
    return partial(utils.create_handler,
                   extractor_factory=extractor_factory,
                   import_module=import_module)

@pytest.mark.parametrize('other_method', HTTP_METHODS)
def test_creates_methods(other_method, mocker):
    """The create_resource should create object with appropriate set of on_xyz methods."""
    handlers = {meth: mocker.Mock() for meth in HTTP_METHODS if meth != other_method}
    resource = create_resource(handlers)
    assert all(hasattr(resource, 'on_' + meth.lower()) for meth in handlers)
    assert not hasattr(resource, 'on_' + other_method.lower())

def test_dispatches_to_handlers(mocker):
    """The object returned by create_resource should forward calls to on_xyz methods to handlers."""
    handlers = {meth: mocker.Mock() for meth in HTTP_METHODS}
    resource = create_resource(handlers)
    req = mocker.Mock()
    resp = mocker.Mock()
    kwargs = {'a': 10, 'b': 'xyz'}
    for meth in handlers:
        getattr(resource, 'on_' + meth.lower())(req, resp, **kwargs)
    for handler in handlers.values():
        handler.handle_request.assert_called_once_with(req, resp, **kwargs)

def test_creates_body_extractor(create_handler, extractor_factory):
    """The create_handler function should create body extractor if its needed."""
    handler = create_handler('some/path', OP_SPEC)
    extractor_factory.build_body_extractor.assert_called_once_with(OP_SPEC['requestBody'])
    assert handler.body_extractor is not None

def test_creates_no_body_extractor(create_handler, extractor_factory):
    """The create_handler function should not create body extractor if its not needed."""
    handler = create_handler('pet/all', BODYLESS_OP_SPEC)
    extractor_factory.build_body_extractor.assert_not_called()
    assert handler.body_extractor is None

def test_creates_param_extractors(create_handler, extractor_factory):
    """The create_handler function should create parameter extractor for every param."""
    handler = create_handler('order/details', OP_SPEC)
    assert extractor_factory.build_param_extractor.call_count == len(OP_SPEC['parameters'])
    for param_spec in OP_SPEC['parameters']:
        extractor_factory.build_param_extractor.assert_any_call(param_spec)
    assert len(handler.params_extractors) == len(OP_SPEC['parameters'])

def test_returns_handler_with_body(create_handler):
    """The create_handler should return corret handler for operation with request body."""
    handler = create_handler('order/details', OP_SPEC)
    assert handler.path == 'order/details'
    assert len(handler.params_extractors) == 2
    assert handler.body_extractor is not None

def test_loads_operation(create_handler, import_module):
    handler = create_handler('some/path', OP_SPEC)
    import_module.assert_called_once_with('my.module')
    assert handler.operation == import_module.return_value.operation
