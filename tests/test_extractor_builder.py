"""Test cases for ParameterBuilder."""
import copy
from nadia.api import SchemaBuilder
import pytest
from aubergine.decoders import PlainDecoder, JSONDecoder
from aubergine.extractors import (ExtractorBuilder, HeaderExtractor, PathExtractor,
                                  QueryExtractor, UnsupportedContentTypeError)


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

def make_param_spec_with_location(param_spec, location):
    """Copy given parameter specification and add location ('in' property) to it."""
    new_spec = copy.deepcopy(param_spec)
    new_spec['in'] = location
    return new_spec

@pytest.fixture(name='schema_builder')
def schema_builder_factory(mocker):
    """Fixture providing mock of SchemaBuilder."""
    return mocker.create_autospec(SchemaBuilder)

@pytest.fixture(name='extractor_builder')
def extractor_builder_factory(schema_builder):
    """Fixture providing an instance of ExtractorBuilder."""
    return ExtractorBuilder(schema_builder)

@pytest.fixture(scope='session', name='simple_parameter_spec', params=['path', 'query', 'header'])
def simple_param_spec_factory(request):
    """Fixture providing various simple (i.e. without conten type)parameter specifications."""
    return make_param_spec_with_location(SIMPLE_PARAMETER_SKELETON, request.param)

@pytest.fixture(scope='session', name='json_parameter_spec', params=['path', 'query', 'header'])
def json_param_spec_factory(request):
    """Fixture providing various parameter specifications with json content type."""
    return make_param_spec_with_location(JSON_PARAMETER_SKELETON, request.param)

def test_uses_plain_decoder(extractor_builder, simple_parameter_spec):
    """ParameterBuilder should use PlainDecoder for parameters defined without content keyword."""
    extractor = extractor_builder.build_param_extractor(simple_parameter_spec)
    assert isinstance(extractor.decoder, PlainDecoder), 'Should use PlainDecoder but does not.'

def test_uses_json_decoder(extractor_builder, json_parameter_spec):
    """ParameterBuilder should uses JSONDecoder for parameters with media application/json."""
    extractor = extractor_builder.build_param_extractor(json_parameter_spec)
    assert isinstance(extractor.decoder, JSONDecoder), 'Should use JSONDecoder but does not.'

@pytest.mark.parametrize('location', ['path', 'query', 'header'])
def test_unsupported_content_type(extractor_builder, location):
    """ParamBuilder should raise UnsupportedContentTypeError if content type is unknown."""
    spec = {
        'name': 'some_param',
        'in': location,
        'content': {
            'application/unknown': {
                'schema': {
                    'type': 'string'
                }
            }
        }
    }
    with pytest.raises(UnsupportedContentTypeError, match='application/unknown'):
        extractor_builder.build_param_extractor(spec)

def test_extractor_types(extractor_builder, simple_parameter_spec):
    """ParamBuilder should base type of constructed extractor on 'in' parameter."""
    extractor = extractor_builder.build_param_extractor(simple_parameter_spec)
    location = simple_parameter_spec['in']

    if location == 'path':
        expected_type = PathExtractor
    elif location == 'query':
        expected_type = QueryExtractor
    elif location == 'header':
        expected_type = HeaderExtractor

    assert expected_type == type(extractor)
