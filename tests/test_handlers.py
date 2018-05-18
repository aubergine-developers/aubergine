"""Test cases for request handlers."""
from falcon import HTTPBadRequest, Request
import pytest
from aubergine.extractors import Extractor, ExtractionResult, MissingValueError, ValidationError
from aubergine.handlers import RequestHandler

def fake_extractor(mocker, present, value):
    """Fake Extractor object whose extract method returns constant results

    :param mocker: a pytest-mocker fixture
    :type mocker: fixture
    :param present: flag equal to the desired value of ExtractionResult.present field
    :type present: bool
    :param value: desired value of ExtractoinResult.value field returned from
     extract method
    :type param: any
    :returns: mock acting as Extractor
    :rtype: mocker.Mock
    """
    ext = mocker.Mock(spec=Extractor)
    ext.extract.return_value = ExtractionResult(present=present, value=value)
    return ext

@pytest.fixture(name='http_req')
def _http_req(mocker):
    return mocker.Mock(spec=Request)

@pytest.fixture(name='operation')
def _operation(mocker):
    """Fixture providing handler operation."""
    return mocker.Mock(return_value='operation body')

def test_extracts_params(mocker, operation, http_req):
    """RequestHandler.get_parameter_dict should use its extractors and return extracted values."""
    body_extractor = fake_extractor(mocker, True, {'name': 'Lessie'})
    param_extractors = {
        'id': fake_extractor(mocker, True, '10'),
        'limit': fake_extractor(mocker, True, 12)}

    handler = RequestHandler(operation=operation,
                             path='pet/detaiis/{petid}',
                             body_extractor=body_extractor,
                             params_extractors=param_extractors)

    kwargs = {'id': 'some_value', 'test': 'test123'}

    params = handler.get_parameter_dict(http_req, **kwargs)

    for extractor in param_extractors.values():
        extractor.extract.assert_called_once_with(http_req, **kwargs)

    body_extractor.extract.assert_not_called()

    assert {'id': '10', 'limit': 12} == params

def test_calls_operation(operation, http_req, mocker):
    """Test that the underlying operation is called correctly."""
    body_extractor = fake_extractor(mocker, True, {'name': 'Lessie'})
    param_extractors = {
        'id': fake_extractor(mocker, True, '10'),
        'limit': fake_extractor(mocker, True, 12)}
    handler = RequestHandler(path='posts/',
                             operation=operation,
                             body_extractor=body_extractor,
                             params_extractors=param_extractors)
    kwargs = {'id': 'some_value', 'test': 'test123'}
    handler.handle_request(http_req, mocker.Mock(), **kwargs)

    expected_call_args = {name: ext.extract.return_value.value
                          for name, ext in param_extractors.items()}
    expected_call_args['body'] = body_extractor.extract.return_value.value
    operation.assert_called_once_with(**expected_call_args)

def test_calls_operation_no_body(operation, http_req, mocker):
    """Test that the underlying operation is called correctly for endpoint with no body."""
    param_extractors = {
        'id': fake_extractor(mocker, True, '10'),
        'limit': fake_extractor(mocker, True, 12)}
    handler = RequestHandler(
        path='path/to/resource',
        operation=operation,
        body_extractor=None,
        params_extractors=param_extractors)
    kwargs = {'id': 'some_value', 'test': 'test123'}
    handler.handle_request(http_req, mocker.Mock(), **kwargs)

    expected_call_args = {name: ext.extract.return_value.value
                          for name, ext in param_extractors.items()}
    operation.assert_called_once_with(**expected_call_args)

def test_raises_bad_request(operation, http_req, mocker):
    """Test that the RequestHandler raises 404 error when param is missing or fails to validate."""
    body_extractor = fake_extractor(mocker, False, None)
    param_extractors = {
        'id': fake_extractor(mocker, True, '10'),
        'limit': fake_extractor(mocker, True, 12)}
    bad_extractor = mocker.Mock(spec=Extractor)
    bad_extractor.extract.side_effect = MissingValueError('header', 'page')
    param_extractors['page'] = bad_extractor
    handler = RequestHandler(
        path='some/path/to/handle',
        operation=operation,
        body_extractor=body_extractor,
        params_extractors=param_extractors)
    kwargs = {'id': 'some_value', 'test': 'test123'}
    with pytest.raises(HTTPBadRequest):
        handler.handle_request(http_req, mocker.Mock(), **kwargs)

    param_extractors['page'].extract = mocker.Mock(side_effect=ValidationError({}))

    with pytest.raises(HTTPBadRequest):
        handler.handle_request(http_req, mocker.Mock(), **kwargs)
