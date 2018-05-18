"""Test cases for content extractors."""
from falcon import HTTPBadRequest, Request
from marshmallow import Schema, UnmarshalResult
import pytest
from aubergine.extractors import (Extractor, read_body, read_header, read_path, read_query,
                                  Location, MissingValueError, ValidationError)


@pytest.fixture(name='http_req')
def _http_req(mocker):
    """Fixture providing HTTP Request mock."""
    return mocker.Mock(spec=Request)

@pytest.fixture(name='schema')
def _schema(mocker):
    """Fixture providing Marshmallow Schema mock."""
    schema = mocker.Mock(spec=Schema)
    schema.load.return_value = {'content': {'foo': 'bar'}}, {}
    return schema

@pytest.fixture(name='decoder')
def _decoder(mocker):
    """Fixture providing decoder mock."""
    return mocker.Mock()

def test_read_body(http_req):
    """The read_body function should obtain data from request's body."""
    body = read_body(http_req)
    http_req.bounded_stream.read.assert_called_once_with()
    assert http_req.bounded_stream.read() == body

def test_raises_missing_body(http_req):
    """The read_body function should raise MissingValueError when body is not present."""
    http_req.bounded_stream.read.return_value = ''
    with pytest.raises(MissingValueError) as exc_info:
        read_body(http_req)
    assert exc_info.value.location == Location.BODY

def test_read_header(http_req):
    """The read_header function should read correct header from request."""
    effect = lambda key, required: {'param1': 'xyz', 'param2': 'uvw'}.get(key)
    http_req.get_header.side_effect = effect
    assert read_header(http_req, 'param1') == 'xyz'
    http_req.get_header.assert_called_once_with('param1', required=True)

def test_raises_missing_header(http_req):
    """The read_header function should raise MissingValueError if given header is missing."""
    http_req.get_header.side_effect = HTTPBadRequest()
    with pytest.raises(MissingValueError) as exc_info:
        read_header(http_req, 'id')
    assert exc_info.value.location == Location.HEADER
    assert exc_info.value.name == 'id'

def test_read_path(http_req):
    """The read_path function should get path argument from kwargs."""
    assert read_path(http_req, param_name='b', a='baz', b='foobar') == 'foobar'

def test_raises_missing_path(http_req):
    """The read_path function should raise MissingValueError if param_name is not in kwargs."""
    with pytest.raises(MissingValueError) as exc_info:
        read_path(http_req, param_name='name', id='10')
    assert exc_info.value.location == Location.PATH
    assert exc_info.value.name == 'name'

def test_read_query(http_req):
    """The read_query function should read correct param from request."""
    assert http_req.get_param.return_value == read_query(http_req, param_name='horror')
    http_req.get_param.assert_called_once_with('horror', required=True)

def test_raises_missing_query(http_req):
    """The read_query function should raise MissingValueError if param_name is not in request."""
    http_req.get_param.side_effect = HTTPBadRequest()
    with pytest.raises(MissingValueError) as exc_info:
        read_query(http_req, param_name='test')
    assert exc_info.value.location == Location.QUERY
    assert exc_info.value.name == 'test'

def test_raises_missing_required(http_req, schema, decoder, mocker):
    """The Extractor.extract should reraise if its param is required and not present."""
    err = MissingValueError(Location.PATH, 'foo')
    read_data = mocker.Mock(side_effect=err)
    ext = Extractor(schema=schema, decoder=decoder, required=True, read_data=read_data)
    with pytest.raises(MissingValueError) as exc_info:
        ext.extract(http_req)
    assert exc_info.value == err

def test_not_raises_optional(http_req, schema, decoder, mocker):
    """The Extractor.extract should not reraise if its param is optional and not present."""
    read_data = mocker.Mock(side_effect=MissingValueError(Location.QUERY, 'foo'))
    ext = Extractor(schema=schema, decoder=decoder, required=False, read_data=read_data)
    result = ext.extract(http_req)
    assert not result.present

def test_returns_loaded_value(http_req, schema, decoder, mocker):
    """The Extractor.extract should decode raw value, pass it to Schema and return parsed value."""
    read_data = mocker.Mock()
    ext = Extractor(schema=schema, decoder=decoder, required=True, read_data=read_data)
    result = ext.extract(http_req)
    decoder.decode.assert_called_once_with(read_data.return_value)
    schema.load.assert_called_once_with({'content': decoder.decode.return_value})
    assert result.present
    assert result.value == schema.load.return_value[0]['content']

def test_uses_read_data(http_req, schema, decoder, mocker):
    """The raw data obtained by Extractor.extract should be get from its read_data function."""
    read_data = mocker.Mock()
    ext = Extractor(schema=schema, decoder=decoder, required=True, read_data=read_data)
    ext.extract(http_req, a='foo', x='bar')
    read_data.assert_called_once_with(http_req, a='foo', x='bar')

def test_raises_validation_error(http_req, decoder, mocker):
    """Extractor.extract should raise ValidationError if validation of decoded data failed."""
    read_data = mocker.Mock()
    schema = mocker.Mock()
    schema.load.return_value = UnmarshalResult({}, [{'test': 'error_msg'}])
    ext = Extractor(schema=schema, decoder=decoder, required=True, read_data=read_data)
    with pytest.raises(ValidationError) as exc_info:
        ext.extract(http_req)
    assert exc_info.value.errors == [{'test': 'error_msg'}]
