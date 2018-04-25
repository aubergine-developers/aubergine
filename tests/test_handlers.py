"""Test cases for request handlers."""
import pytest
from aubergine import extractors
from aubergine.handlers import RequestHandler


@pytest.fixture(name='body_extractor')
def mock_body_extractor(mocker):
    """Fixture providing body extractor's mock."""
    return mocker.create_autospec(extractors.BodyExtractor)

@pytest.fixture(name='path_extractor')
def mock_path_extractor(mocker):
    """Fixture providing path extractor's mock."""
    return mocker.Mock()

@pytest.fixture(name='query_extractor')
def mock_query_extractor(mocker):
    """Fixture providing query extractor's mock."""
    return mocker.Mock()

def test_handler_extracts_params(body_extractor, path_extractor, query_extractor, mocker):
    """RequestHandler.get_parameter_dict should use its extractors and return extracted values."""
    handler = RequestHandler(mocker.Mock(), body_extractor, [path_extractor, query_extractor])
    req = mocker.Mock()
    path_extractor.param_name = 'param1'
    query_extractor.param_name = 'param2'
    params = handler.get_parameter_dict(req, test=123, test2='test')
    path_extractor.extract.assert_called_once_with(req, test=123, test2='test')
    query_extractor.extract.assert_called_once_with(req, test=123, test2='test')
    assert params == {'param1': path_extractor.extract.return_value,
                      'param2': query_extractor.extract.return_value}
