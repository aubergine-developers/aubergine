"""Common fixtures for aubergine unit tests."""
import json
import pytest
from aubergine.extractors import HeaderExtractor, QueryExtractor, PathExtractor, BodyExtractor


def extractor_spy(mocker, extractor):
    """Patch an extractor to be able to spy on its 'extract' method.

    :param mocker: a mocker fixture
    :type mocker: mocker fixture
    :param extractor: an extractor to patch
    :type extractor: :py:class:`aubergine.extractors.Extractor`
    :returns: patched extractor
    :rtype: :py:class:`aubergine.extractors.Extractor`
    """
    mocker.spy(extractor, 'extract')
    return extractor

@pytest.fixture(name='schema')
def _schema(mocker):
    schema = mocker.Mock()
    schema.load.return_value = {'content': mocker.Mock()}
    return schema

@pytest.fixture(name='sample_data')
def sample_data_provider():
    """Sample data for stubbing request.bounded_stream."""
    data = {'petId': 100, 'petName': 'Burek', 'owner': {'firstName': 'John', 'lastName': 'Doe'}}
    return json.dumps(data)

@pytest.fixture(name='http_request')
def get_http_request(mocker, sample_data):
    """Fixture providing sample http_request."""
    req = mocker.Mock()
    req.bounded_stream = mocker.Mock()
    req.bounded_stream.read.return_value = sample_data
    req.get_header.side_effect = {'head1': 'somevalue', 'head2': 'someothervalue'}.get
    req.get_param.side_effect = {'foo': 'bar', 'fizz': 2137}.get
    return req

def make_extractor_mock(mocker, mock_type, param_name=None):
    extractor = mocker.Mock(spec=mock_type)
    if param_name is not None:
        extractor.param_name = param_name
    return extractor

@pytest.fixture(name='header_extractor', params=['head1', 'head2'], scope='function')
def header_extractor_factory(request, mocker):
    """Fixture providing instance of HeaderExtractor with decoder and schema mocked."""
    return make_extractor_mock(mocker, HeaderExtractor, request.param)

@pytest.fixture(name='path_extractor', params=['id', 'user'], scope='function')
def path_extractor_factory(request, mocker):
    """Fixture providing instances of PathExtractor with decoder and schema mocked."""
    return make_extractor_mock(mocker, PathExtractor, request.param)

@pytest.fixture(name='query_extractor', params=['foo', 'fizz'])
def query_extractor_factory(request, mocker):
    """Fixture providing instances of QueryExtractor."""
    return make_extractor_mock(mocker, QueryExtractor, request.param)

@pytest.fixture(name='body_extractor')
def body_extractor_factory(mocker):
    """Fixtrure providing an instance ofBodyExtractor with decoder and schema mocked."""
    extractor = mocker.Mock(spec=BodyExtractor)
    return extractor
