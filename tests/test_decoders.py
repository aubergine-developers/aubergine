"""Test cases for content decoders."""
import json
import pytest
from aubergine import decoders


@pytest.fixture(name='json_loads')
def get_json_loads(mocker):
    """Return an object spying on json.loads."""
    return mocker.spy(json, 'loads')

@pytest.fixture(name='json_decoder')
def get_json_decoder():
    """Fixture returning JSONDecoder for the purpose of testing."""
    return decoders.JSONDecoder()

@pytest.fixture(name='plain_decoder')
def plain_decoder_factory():
    """Fixture returning PlainDecoder instance for the purpose of testing."""
    return decoders.PlainDecoder()

def test_json_decoder_decodes_str(json_decoder, json_loads):
    """JSONDecoder.decode should correctly decode json-encoded strings."""
    str_json_data = json.dumps({'petId': 100, 'petName': 'Azor'})
    decoded = json_decoder.decode(str_json_data)
    assert decoded == {'petId': 100, 'petName': 'Azor'}
    json_loads.assert_called_once_with(str_json_data)

def test_json_decoder_decodes_bytes(json_decoder, json_loads):
    """JSONDecoder.decode should correctly decode json-encoded bytes."""
    bytes_json_data = json.dumps({'petId': 100, 'petName': 'Azor'}).encode('utf-8')
    decoded = json_decoder.decode(bytes_json_data)
    assert decoded == {'petId': 100, 'petName': 'Azor'}
    json_loads.assert_called_once_with(bytes_json_data)

def test_json_decoder_raises(json_decoder):
    """JSONDecoder.decode should raise DecodingError when JSON decoding failed."""
    invalid_data = '{"b": fail'
    with pytest.raises(decoders.DecodingError):
        json_decoder.decode(invalid_data)

@pytest.mark.parametrize('content', ['somecontent', b'somecontent'])
def test_plain_decoder_decodes(plain_decoder, content):
    """Test that PlainDecoder.decode works as an identity map."""
    assert plain_decoder.decode(content) == content
