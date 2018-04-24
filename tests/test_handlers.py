"""Test cases for request handlers."""
import pytest
from aubergine import extractors
from aubergine.extractors import ParameterValidationError
from aubergine.handlers import RequestHandler


@pytest.fixture
def body_extractor(mocker):
    return mocker.Mock()

@pytest.fixture
def path_extractor(mocker):
    return mocker.Mock()

@pytest.fixture
def query_extractor(mocker):
    return mocker.Mock()

def test_handler_extracts_params(body_extractor, path_extractor, query_extractor, mocker):
    """RequestHandler.get_parameter_dict should use its extractors and return extracted values."""
    handler = RequestHandler(mocker.Mock(), body_extractor, [path_extractor, query_extractor])
    req = mocker.Mock()
    path_extractor.param_name = 'param1'
    query_extractor.param_name = 'param2'
    params = handler.get_parameter_dict(req, test=123, test2='test')
    path_extractor.extract.assert_called_once_with(req, test=123,test2='test')
    query_extractor.extract.assert_called_once_with(req, test=123,test2='test')
    assert params == {'param1': path_extractor.extract.return_value,
                      'param2': query_extractor.extract.return_value}
