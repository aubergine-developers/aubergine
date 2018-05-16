"""Test cases for ParameterBuilder."""
import copy
from nadia.api import SchemaBuilder
import pytest
from aubergine.decoders import PlainDecoder, JSONDecoder
from aubergine.extractors import (ExtractorBuilder, read_header, read_query,
                                  read_body, read_path, UnsupportedContentTypeError)


SIMPLE_PARAMETER_SKELETON = {'name': 'some_param', 'schema': {'type': 'string'}}

JSON_PARAMETER_SKELETON = {
    'name': 'some_param',
    'content': {
        'application/json': {
            'schema': {
                'type': 'number'
            }
        }
    }
}

EXPECTED_READERS = {'path': read_path, 'header': read_header, 'query': read_query}

def make_param_spec(param_spec, location):
    """Copy given parameter specification and add location ('in' property) to it."""
    new_spec = copy.deepcopy(param_spec)
    new_spec['in'] = location
    return new_spec

@pytest.fixture(name='schema_builder')
def _schema_builder(mocker):
    """Fixture providing mock of SchemaBuilder."""
    return mocker.create_autospec(SchemaBuilder)

@pytest.fixture(name='extractor_factory')
def _extractor_factory(schema_builder):
    """Fixture providing an instance of ExtractorBuilder."""
    return ExtractorBuilder(schema_builder)

@pytest.fixture(scope='session', name='simple_spec', params=['path', 'query', 'header'])
def _simple_spec(request):
    """Fixture providing various simple (i.e. without conten type)parameter specifications."""
    return make_param_spec(SIMPLE_PARAMETER_SKELETON, request.param)

@pytest.fixture(scope='session', name='json_spec', params=['path', 'query', 'header'])
def _json_spec(request):
    """Fixture providing various parameter specifications with json content type."""
    return make_param_spec(JSON_PARAMETER_SKELETON, request.param)

def test_uses_plain_decoder(schema_builder, simple_spec):
    """ParameterBuilder should use PlainDecoder for parameters defined without content keyword."""
    builder = ExtractorBuilder(schema_builder)
    extractor = builder.build_param_extractor(simple_spec)
    assert isinstance(extractor.decoder, PlainDecoder), 'Should use PlainDecoder but does not.'

def test_uses_json_decoder(schema_builder, json_spec):
    """ParameterBuilder should uses JSONDecoder for parameters with media application/json."""
    builder = ExtractorBuilder(schema_builder)
    extractor = builder.build_param_extractor(json_spec)
    assert isinstance(extractor.decoder, JSONDecoder)
    extractor = builder.build_body_extractor({'content': json_spec['content']})
    assert isinstance(extractor.decoder, JSONDecoder)

def test_unsupported_content_type(schema_builder):
    """ParamBuilder should raise UnsupportedContentTypeError if content type is unknown."""
    builder = ExtractorBuilder(schema_builder)
    spec = {'content': {'application/unknown': {'schema': {'type': 'number'}}}}
    with pytest.raises(UnsupportedContentTypeError, match='application/unknown'):
        builder.build_body_extractor(spec)
    spec['in'] = 'path'
    spec['name'] = 'id'
    with pytest.raises(UnsupportedContentTypeError, match='application/unknown'):
        builder.build_param_extractor(spec)

def test_extractor_types(schema_builder, simple_spec):
    """ParamBuilder should base type of constructed extractor on 'in' parameter."""
    builder = ExtractorBuilder(schema_builder)
    extractor = builder.build_param_extractor(simple_spec)
    assert extractor.read_data.func == EXPECTED_READERS[simple_spec['in']]

def test_body_extractor_reader(schema_builder, json_spec):
    """Extractorbuilder should build extractors equiped with correct reader."""
    builder = ExtractorBuilder(schema_builder)
    extractor = builder.build_body_extractor({'content': json_spec['content']})
    assert extractor.read_data == read_body
