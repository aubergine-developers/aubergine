"""Test cases for content decoders."""
import json
import pytest
from aubergine.common import Loggable
from aubergine import decoders


@pytest.fixture(scope='function')
def json_loads(mocker):
    """Return an object spying on json.loads."""
    return mocker.spy(json, 'loads')

@pytest.fixture
def json_decoder():
    """Fixture returning JSONDecoder for the purpose of testing."""
    return decoders.JSONDecoder()

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

def test_json_decoder_raises_decoding_error(json_decoder):
    """JSONDecoder.decode should raise DecodingError when JSON decoding failed."""
    invalid_data = '{"b": fail'
    with pytest.raises(decoders.DecodingError):
        json_decoder.decode(invalid_data)
