"""Test cases for content extractors."""
from marshmallow import UnmarshalResult, Schema
import pytest
from aubergine.extractors import (Extractor, BodyExtractor, Location, ParameterMissingError,
                                  HeaderExtractor, QueryExtractor, PathExtractor)


class DummyExtractor(Extractor):
    """Dummy extractor for the purpose of testing abstract Extractor class."""

    @staticmethod
    def read_data(req, **kwargs):
        pass

@pytest.fixture(name='schema')
def _schema(mocker):
    schema = mocker.Mock(spec=Schema)
    schema.load.return_value = UnmarshalResult({'content': mocker.Mock()}, [])
    return schema

@pytest.fixture(name='dummy_extractor')
def get_dummy_extractor(schema, mocker):
    """Fixture providing simple Extractor object."""
    extractor = DummyExtractor(schema, mocker.Mock())
    mocker.patch.object(extractor, 'read_data')
    return extractor

def test_extractor_decodes_data(dummy_extractor, http_request):
    """Extractor.extract should read data and decode them using correct decoder."""
    dummy_extractor.extract(http_request)
    dummy_extractor.decoder.decode.assert_called_once_with(dummy_extractor.read_data())

def test_extractor_loads_data(dummy_extractor, http_request):
    """Extractor.extract should pass decoded data to Extractor's schema."""
    data = dummy_extractor.extract(http_request)
    assert data == dummy_extractor.schema.load.return_value.data['content']
    expected_arg = {'content': dummy_extractor.decoder.decode.return_value}
    dummy_extractor.schema.load.assert_called_once_with(expected_arg)

def test_reads_bounded_stream(mocker, http_request):
    """BodyExtractor.read_data should read data from http_request.bounded_stream."""
    body_extractor = BodyExtractor(mocker.Mock(), mocker.Mock())
    content = body_extractor.read_data(http_request)
    assert content == http_request.bounded_stream.read.return_value
    http_request.bounded_stream.read.assert_called_once_with()

def test_reads_header(schema, http_request, mocker):
    """HeaderExtractor.read_data should read data using http_request.get_header."""
    ext = HeaderExtractor(schema, mocker.Mock(), 'head1', True)
    content = ext.read_data(http_request)
    http_request.get_header.assert_called_once_with(ext.param_name)
    assert content == http_request.get_header(ext.param_name)

def test_reads_param(schema, http_request, mocker):
    """QueryExtractor.read_data should read correct query parameter."""
    ext = QueryExtractor(schema, mocker.Mock(), 'fizz', True)
    content = ext.read_data(http_request)
    http_request.get_param.assert_called_once_with(ext.param_name)
    assert content == http_request.get_param(ext.param_name)

@pytest.mark.parametrize('kwvalue', ['foo', 'bar'])
def test_path_extractor(schema, http_request, kwvalue, mocker):
    """PathExtractor.read_data should extract correct path parameter given in kwargs."""
    ext = PathExtractor(schema, mocker.Mock(), 'head1')
    kwargs = {ext.param_name: kwvalue, 'other_arg': 'other_value'}
    content = ext.read_data(http_request, **kwargs)
    assert content == kwvalue

def test_path_extractor_raises(schema, http_request, mocker):
    """PathExtractor.read_data should raise ParameterMissingError when parameter is missing."""
    ext = PathExtractor(schema, mocker.Mock(), 'head1')
    kwargs = {ext.param_name + 'asdf': 'test'}
    with pytest.raises(ParameterMissingError) as excinfo:
        ext.read_data(http_request, **kwargs)

    assert excinfo.value.location == Location.PATH
    assert excinfo.value.name == ext.param_name

    with pytest.raises(ParameterMissingError) as excinfo:
        ext.read_data(http_request)

    assert excinfo.value.location == Location.PATH
    assert excinfo.value.name == ext.param_name
