"""Test cases for operations module."""
import importlib
import pytest
from aubergine.operations import OperationLoader, InvalidOperationPathError, NotCallableError


@pytest.fixture(name='import_module', scope='function')
def _import_module(mocker):
    """Factory providing mocked import_module."""
    return mocker.create_autospec(importlib.import_module)

def test_loads_correct_module(import_module):
    """OperationLoader.load should load correct module"""
    op_loader = OperationLoader(import_module)
    path = 'my.module.foo'
    func = op_loader.load(path)
    import_module.assert_called_once_with('my.module')

def test_gets_correct_function(import_module):
    """OperationLoader.load should get correct function from loaded module."""
    op_loader = OperationLoader(import_module)
    path = 'my.module.foo'
    func = op_loader.load(path)
    assert func == import_module('my.module').foo

def test_raises_if_path_invalid(import_module):
    """OperationLoader.load should raise InvalidOperationError for invalid path."""
    op_loader = OperationLoader(import_module)
    with pytest.raises(InvalidOperationPathError):
        func = op_loader.load('myinvalidpathfoo')

@pytest.mark.parametrize('attr', [1, 'test', [1, 2, '3']])
def test_raises_if_not_callble(attr, import_module):
    """OperationLoader.load should raise NotCallableError if loaded objectn is not callable."""
    import_module.return_value.bar = attr
    op_loader = OperationLoader(import_module)
    with pytest.raises(NotCallableError) as errinfo:
        op_loader.load('module.bar')
    assert 'module.bar' in str(errinfo.value)
