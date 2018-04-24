"""Test cases for content extractors."""
import json
import pytest
from aubergine import extractors


class DummyExtractor(extractors.Extractor):
    """Dummy extractor for the purpose of testing abstract Extractor class."""

    @staticmethod
    def read_data(_req, **kwargs):
        pass

@pytest.fixture
def dummy_extractor(mocker):
    """Fixture providing simple Extractor object."""
    extractor = DummyExtractor(mocker.Mock(), mocker.Mock())
    mocker.patch.object(extractor, 'read_data')
    return extractor

@pytest.fixture
def sample_data():
    """Sample data for stubbing request.bounded_stream."""
    data = {'petId': 100, 'petName': 'Burek', 'owner': {'firstName': 'John', 'lastName': 'Doe'}}
    return json.dumps(data)

@pytest.fixture
def http_request(mocker, sample_data):
    """Fixture providing sample http_request."""
    req = mocker.Mock()
    req.bounded_stream = mocker.Mock()
    req.bounded_stream.read.return_value = sample_data
    req.get_header.side_effect = {'head1': 'somevalue', 'head2': 'someothervalue'}.get
    req.get_param.side_effect = {'foo': 'bar'}.get
    return req

@pytest.fixture
def header_extractor_factory(mocker):
    def _create_header_extractor(header_name, required=False):
        return extractors.HeaderExtractor(mocker.Mock(), mocker.Mock(), header_name, required)
    return _create_header_extractor

@pytest.fixture
def path_extractor_factory(mocker):
    """Fixture providing factory methods for constructing PathExtractors with given param_name."""
    def _create_path_extractor(param_name):
        return extractors.PathExtractor(mocker.Mock(), mocker.Mock(), param_name)
    return _create_path_extractor

@pytest.fixture
def query_extractor_factory(mocker):
    """Fixture providing factory methods for constructing QueryExtractors with given param_name."""
    def _create_query_extractor(param_name, required=False):
        return extractors.QueryExtractor(mocker.Mock(), mocker.Mock(), param_name, required)
    return _create_query_extractor

@pytest.fixture
def body_extractor(mocker):
    """Fixtrure providing an instance of BodyExtractor with decoder and schema mocked."""
    return extractors.BodyExtractor(mocker.Mock(), mocker.Mock())

def test_extractor_decodes_read_data(dummy_extractor, http_request):
    """Extractor.extract should read data and decode them using correct decoder."""
    dummy_extractor.extract(http_request)
    dummy_extractor.decoder.decode.assert_called_once_with(dummy_extractor.read_data())

def test_extractor_loads_decoded_data(dummy_extractor, http_request):
    """Extractor.extract should pass decoded data to Extractor's schema."""
    data = dummy_extractor.extract(http_request)
    assert data == dummy_extractor.schema.load.return_value
    expected_arg = {'content': dummy_extractor.decoder.decode.return_value}
    dummy_extractor.schema.load.assert_called_once_with(expected_arg)

def test_body_extractor_reads_content(body_extractor, http_request):
    """BodyExtractor.read_data should read data from http_request.bounded_stream."""
    content = body_extractor.read_data(http_request)
    assert content == http_request.bounded_stream.read.return_value
    http_request.bounded_stream.read.assert_called_once_with()

def test_header_extractor_reads_correct_header(header_extractor_factory, http_request):
    """HeaderExtractor.read_data should read data using http_request.get_header."""
    extractor = header_extractor_factory('head1')
    content = extractor.read_data(http_request)
    http_request.get_header.assert_called_once_with('head1')
    assert content == http_request.get_header('head1')

def test_query_extractor_reads_correct_param(query_extractor_factory, http_request):
    """QueryExtractor.read_data should read correct query parameter."""
    extractor = query_extractor_factory('foo')
    content = extractor.read_data(http_request)
    http_request.get_param.assert_called_once_with('foo')
    assert content == http_request.get_param('foo')

@pytest.mark.parametrize('kwkey,kwvalue', [('foo', 'bar'), ('baz', 'xyz')])
def test_path_extractor(path_extractor_factory, http_request, kwkey, kwvalue):
    """PathExtractor.read_data should extract correct path parameter given in kwargs."""
    extractor = path_extractor_factory(kwkey)
    content = extractor.read_data(http_request, **{kwkey: kwvalue})
    assert content == kwvalue
