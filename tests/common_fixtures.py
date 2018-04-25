"""Common fixtures for aubergine unit tests."""
import json
import pytest
import marshmallow
from aubergine import extractors


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

@pytest.fixture(name='header_extractor', params=['head1', 'head2'])
def header_extractor_factory(request, mocker):
    """Fixture providing instance of HeaderExtractor with decoder and schema mocked."""
    return extractors.HeaderExtractor(mocker.Mock(), mocker.Mock(), request.param, required=True)

@pytest.fixture(name='path_extractor', params=['id', 'user'])
def path_extractor_factory(request, mocker):
    """Fixture providing instances of PathExtractor with decoder and schema mocked."""
    return extractors.PathExtractor(mocker.Mock(), mocker.Mock(), request.param)

@pytest.fixture(name='query_extractor', params=['foo', 'fizz'])
def query_extractor_factory(request, mocker):
    """Fixture providing instances of QueryExtractor."""
    return extractors.QueryExtractor(mocker.Mock(), mocker.Mock(), request.param, required=True)

@pytest.fixture(name='body_extractor')
def body_extractor_factory(mocker):
    """Fixtrure providing an instance ofBodyExtractor with decoder and schema mocked."""
    return extractors.BodyExtractor(mocker.Mock(), mocker.Mock())
