"""Test cases for request handlers."""
import pytest
from aubergine.handlers import RequestHandler

@pytest.fixture(name='operation')
def operation_factory(mocker):
    """Fixture providing handler operation."""
    return mocker.Mock(return_value='operation body')

@pytest.fixture(name='param_extractors')
def extractors_factory(path_extractor, query_extractor, header_extractor):
    """Fixture providing instances of all parameter extractors at once."""
    return {'path': path_extractor,
            'query': query_extractor,
            'header': header_extractor}

def test_extracts_params(operation, body_extractor, param_extractors, http_request, mocker):
    """RequestHandler.get_parameter_dict should use its extractors and return extracted values."""
    handler = RequestHandler(operation, body_extractor, list(param_extractors.values()))
    kwargs = {param_extractors['path'].param_name: 'some_value', 'test': 'test123'}

    mocker.spy(body_extractor, 'extract')
    for extractor in param_extractors.values():
        mocker.spy(extractor, 'extract')

    params = handler.get_parameter_dict(http_request, **kwargs)

    for extractor in param_extractors.values():
        extractor.extract.assert_called_once_with(http_request, **kwargs)

    body_extractor.extract.assert_not_called()

    query_extractor = param_extractors['query']
    header_extractor = param_extractors['header']
    path_extractor = param_extractors['path']

    assert params == {
        header_extractor.param_name: header_extractor.schema.load.return_value,
        query_extractor.param_name: query_extractor.schema.load.return_value,
        path_extractor.param_name: path_extractor.schema.load.return_value}
