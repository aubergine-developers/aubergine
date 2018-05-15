"""Test cases for content extractors."""
from falcon import HTTPBadRequest, Request
import pytest
from aubergine.extractors import (read_body, read_header, read_path, read_query,
                                  Location, MissingValueError)


@pytest.fixture(name='http_req')
def _http_req(mocker):
    return mocker.Mock(spec=Request)

def test_read_body(http_req):
    body = read_body(http_req)
    http_req.bounded_stream.read.assert_called_once_with()
    assert http_req.bounded_stream.read() == body

def test_raises_missing_body(http_req):
    http_req.bounded_stream.read.return_value = ''
    with pytest.raises(MissingValueError) as exc_info:
        read_body(http_req)
    assert exc_info.value.location == Location.BODY

def test_read_header(http_req):
    effect= lambda key, required: {'param1': 'xyz', 'param2': 'uvw'}.get(key)
    http_req.get_header.side_effect = effect
    assert 'xyz' == read_header(http_req, 'param1')
    http_req.get_header.assert_called_once_with('param1', required=True)

def test_raises_missing_header(http_req):
    http_req.get_header.side_effect = HTTPBadRequest()
    with pytest.raises(MissingValueError) as exc_info:
        read_header(http_req, 'id')
    assert exc_info.value.location == Location.HEADER
    assert exc_info.value.name == 'id'

def test_read_path(http_req):
    assert 'foobar' == read_path(http_req, param_name='b', a='baz', b='foobar')

def test_raises_missing_path(http_req):
    with pytest.raises(MissingValueError) as exc_info:
        read_path(http_req, param_name='name', id='10')
    assert exc_info.value.location == Location.PATH
    assert exc_info.value.name == 'name'

def test_read_query(http_req):
    assert http_req.get_param.return_value == read_query(http_req, param_name='horror')
    http_req.get_param.assert_called_once_with('horror', required=True)

def test_raises_missing_query(http_req):
    http_req.get_param.side_effect = HTTPBadRequest()
    with pytest.raises(MissingValueError) as exc_info:
        read_query(http_req, param_name='test')
    assert exc_info.value.location == Location.QUERY
    assert exc_info.value.name == 'test'
