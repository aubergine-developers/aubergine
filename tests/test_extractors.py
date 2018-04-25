"""Test cases for content extractors."""
import pytest
from aubergine import extractors


class DummyExtractor(extractors.Extractor):
    """Dummy extractor for the purpose of testing abstract Extractor class."""

    @staticmethod
    def read_data(_req, **kwargs):
        pass

@pytest.fixture(name='dummy_extractor')
def get_dummy_extractor(mocker):
    """Fixture providing simple Extractor object."""
    extractor = DummyExtractor(mocker.Mock(), mocker.Mock())
    mocker.patch.object(extractor, 'read_data')
    return extractor

def test_extractor_decodes_data(dummy_extractor, http_request):
    """Extractor.extract should read data and decode them using correct decoder."""
    dummy_extractor.extract(http_request)
    dummy_extractor.decoder.decode.assert_called_once_with(dummy_extractor.read_data())

def test_extractor_loads_data(dummy_extractor, http_request):
    """Extractor.extract should pass decoded data to Extractor's schema."""
    data = dummy_extractor.extract(http_request)
    assert data == dummy_extractor.schema.load.return_value
    expected_arg = {'content': dummy_extractor.decoder.decode.return_value}
    dummy_extractor.schema.load.assert_called_once_with(expected_arg)

def test_reads_bounded_stream(body_extractor, http_request):
    """BodyExtractor.read_data should read data from http_request.bounded_stream."""
    content = body_extractor.read_data(http_request)
    assert content == http_request.bounded_stream.read.return_value
    http_request.bounded_stream.read.assert_called_once_with()

def test_reads_header(header_extractor, http_request):
    """HeaderExtractor.read_data should read data using http_request.get_header."""
    content = header_extractor.read_data(http_request)
    http_request.get_header.assert_called_once_with(header_extractor.param_name)
    assert content == http_request.get_header(header_extractor.param_name)

def test_reads_param(query_extractor, http_request):
    """QueryExtractor.read_data should read correct query parameter."""
    content = query_extractor.read_data(http_request)
    http_request.get_param.assert_called_once_with(query_extractor.param_name)
    assert content == http_request.get_param(query_extractor.param_name)

@pytest.mark.parametrize('kwvalue', ['foo', 'bar'])
def test_path_extractor(path_extractor, http_request, kwvalue):
    """PathExtractor.read_data should extract correct path parameter given in kwargs."""
    kwargs = {path_extractor.param_name: kwvalue, 'other_arg': 'other_value'}
    content = path_extractor.read_data(http_request, **kwargs)
    assert content == kwvalue

def test_path_extractor_raises(path_extractor, http_request):
    """PathExtractor.read_data should raise ParameterMissingError when parameter is missing."""
    kwargs = {path_extractor.param_name + 'asdf': 'test'}
    with pytest.raises(extractors.ParameterMissingError) as excinfo:
        path_extractor.read_data(http_request, **kwargs)

    assert excinfo.value.location == extractors.Location.PATH
    assert excinfo.value.name == path_extractor.param_name

    with pytest.raises(extractors.ParameterMissingError) as excinfo:
        path_extractor.read_data(http_request)

    assert excinfo.value.location == extractors.Location.PATH
    assert excinfo.value.name == path_extractor.param_name
