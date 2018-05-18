"""Test cases for create_handler function."""
import importlib
from functools import partial
from nadia.api import SchemaBuilder
import pytest
from aubergine.extractors import ExtractorBuilder
from aubergine import utils


OP_SPEC = {
    'operationId': 'my.module.operation',
    'requestBody': {'content': {'application/json': {'schema': {'type': 'string'}}}},
    'parameters': [
        {'name': 'name', 'in': 'path', 'schema': {'type': 'string'}},
        {'name': 'id', 'in': 'query', 'schema': {'type': 'integer'}}
    ]
}

BODYLESS_OP_SPEC = {key: value for key, value in OP_SPEC.items() if key != 'requestBody'}
PARAMLESS_OP_SPEC = {key: value for key, value in OP_SPEC.items() if key != 'parameters'}
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

def test_creates_no_param_extractor(create_handler, extractor_factory):
    """The create_handler function should not create param extractors when there are no params."""
    handler = create_handler('order/details', PARAMLESS_OP_SPEC)
    assert extractor_factory.build_param_extractor.call_count == 0
    assert not handler.params_extractors

def test_returns_handler_with_body(create_handler):
    """The create_handler should return corret handler for operation with request body."""
    handler = create_handler('order/details', OP_SPEC)
    assert handler.path == 'order/details'
    assert len(handler.params_extractors) == 2
    assert handler.body_extractor is not None

def test_loads_operation(create_handler, import_module):
    """Create handler function should load operation using its import_module."""
    handler = create_handler('some/path', OP_SPEC)
    import_module.assert_called_once_with('my.module')
    assert handler.operation == import_module.return_value.operation
