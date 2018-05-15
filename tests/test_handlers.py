"""Test cases for request handlers."""
import falcon
import pytest
from aubergine.extractors import ParameterMissingError, ParameterValidationError
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

def test_extracts_params(operation, body_extractor, param_extractors, http_request):
    """RequestHandler.get_parameter_dict should use its extractors and return extracted values."""
    handler = RequestHandler(operation=operation,
                             path='pet/detaiis/{petid}',
                             body_extractor=body_extractor,
                             params_extractors=list(param_extractors.values()))
    kwargs = {param_extractors['path'].param_name: 'some_value', 'test': 'test123'}

    params = handler.get_parameter_dict(http_request, **kwargs)

    for extractor in param_extractors.values():
        extractor.extract.assert_called_once_with(http_request, **kwargs)

    body_extractor.extract.assert_not_called()

    query_extractor = param_extractors['query']
    header_extractor = param_extractors['header']
    path_extractor = param_extractors['path']

    assert params == {ext.param_name: ext.extract.return_value
                      for ext in [header_extractor, query_extractor, path_extractor]}


def test_calls_operation(operation, body_extractor, param_extractors, http_request, mocker):
    """Test that the underlying operation is called correctly."""
    handler = RequestHandler(
        path='posts/',
        operation=operation,
        body_extractor=body_extractor,
        params_extractors=list(param_extractors.values()))
    kwargs = {param_extractors['path'].param_name: 'some_value', 'test': 'test123'}
    handler.handle_request(http_request, mocker.Mock(), **kwargs)

    expected_call_args = {extractor.param_name: extractor.extract.return_value
                          for extractor in param_extractors.values()}
    expected_call_args['body'] = body_extractor.extract.return_value
    operation.assert_called_once_with(**expected_call_args)

def test_calls_operation_no_body(operation, param_extractors, http_request, mocker):
    """Test that the underlying operation is called correctly for endpoint with no body."""
    handler = RequestHandler(
        path='path/to/resource',
        operation=operation,
        body_extractor=None,
        params_extractors=list(param_extractors.values()))
    kwargs = {param_extractors['path'].param_name: 'some_value', 'test': 'test123'}
    handler.handle_request(http_request, mocker.Mock(), **kwargs)

    expected_call_args = {extractor.param_name: extractor.extract.return_value
                          for extractor in param_extractors.values()}
    operation.assert_called_once_with(**expected_call_args)

@pytest.mark.parametrize('which', ['header', 'query', 'path'])
def test_raises_bad_request(operation, param_extractors, which, http_request, mocker):
    """Test that the RequestHandler raises 404 error when param is missing or fails to validate."""
    extractor = param_extractors[which]
    extract_mock = mocker.Mock(side_effect=ParameterMissingError(which, extractor.param_name))
    extractor.extract = extract_mock
    handler = RequestHandler(
        path='some/path/to/handle',
        operation=operation,
        body_extractor=None,
        params_extractors=list(param_extractors.values()))
    kwargs = {param_extractors['path'].param_name: 'some_value', 'test': 'test123'}
    with pytest.raises(falcon.HTTPBadRequest):
        handler.handle_request(http_request, mocker.Mock(), **kwargs)

    extract_mock = mocker.Mock(side_effect=ParameterValidationError({}))
    extractor.extract = extract_mock

    with pytest.raises(falcon.HTTPBadRequest):
        handler.handle_request(http_request, mocker.Mock(), **kwargs)
