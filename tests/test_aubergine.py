"""Test case for main Aubergine class."""
import importlib
import falcon
import pytest
import ymlref
from aubergine.extractors import ExtractorBuilder
from aubergine import Aubergine


@pytest.fixture(name='mock_open')
def _mock_open(mocker):
    """Fixture providing mock of open function that "reads" specification in yml format."""
    _open = mocker.mock_open(read_data=SPEC_CONTENT)
    return mocker.patch('aubergine.aubergine.open', _open)

@pytest.fixture(name='spec_dict', scope='session')
def _spec_dict():
    """Fixture providing mapping with API specification content."""
    return ymlref.load(SPEC_CONTENT)

@pytest.fixture(name='ymlref_mock', autouse=True)
def _ymlref_mock(mocker):
    """Fixture providing mock of ymlref module."""
    return mocker.Mock(wraps=ymlref)

@pytest.fixture(name='utils')
def _utils(mocker):
    """Fixture providing mock of aubergine.utils module."""
    return mocker.patch('aubergine.aubergine.utils')

@pytest.fixture(name='extractor_factory')
def _extractor_factory(mocker):
    """Fixture providing ExtractorBuilder mock."""
    return mocker.Mock(spec_set=ExtractorBuilder)

@pytest.fixture(name='import_module')
def _import_module(mocker):
    """Fixture providing importlib.import_module mock."""
    return mocker.Mock(spec_set=importlib.import_module)

@pytest.fixture(name='api_factory')
def _api_factory(mocker):
    """Fixture providing mock of falcon.API instance."""
    return mocker.Mock(spec_set=falcon.API)

def test_from_file(spec_dict, mock_open):
    """Aubergine.from_file should return Aubergine object with spec read from file."""
    app = Aubergine.from_file('myspec_v1.yml')
    mock_open.assert_called_once_with('myspec_v1.yml')
    assert app.spec_dict == spec_dict

def test_creates_handlers(spec_dict, extractor_factory, import_module, utils):
    """Aubergine.build_api should construct all handlers for its specification."""
    app = Aubergine(spec_dict)
    app.build_api(ex_factory=extractor_factory, import_module=import_module)
    utils.create_handler.assert_any_call('/books', spec_dict['paths']['/books']['get'],
                                         extractor_factory, import_module)

def test_respects_base_path(api_factory, extractor_factory, import_module, spec_dict, mocker):
    """Aubergine.build_api should add routes respecting base path."""
    app = Aubergine(spec_dict)
    app.build_api(api_factory, ex_factory=extractor_factory, import_module=import_module)
    api_factory().add_route.assert_called_once_with('/v1/rest/books', mocker.ANY)

SPEC_CONTENT = """
openapi: "3.0.0"
servers:
  - url: /v1/rest
info:
  version: 1.0.0
  title: Bookstore
  description: A sample API for testing aubergine's main class
  termsOfService: http://swagger.io/terms/
  contact:
    name: dexter2206
    email: dexter2206@gmail.com
  license:
    name: MIT
paths:
  /books:
    get:
      operationId: bookstore.get_all
      parameters:
        - name: type
          in: query
          description: genre to filter by
          required: false
          schema:
            type: string
        - name: limit
          in: query
          description: maximum number of books to return
          required: false
          schema:
            type: integer
            format: int32
      responses:
        '200':
          description: book response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Book'
        default:
          description: unexpected error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
    post:
      description: Creates a new book in the store.
      operationId: bookstore.add_book
      requestBody:
        description: Book to add to the store
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NewBook'
      responses:
        '200':
          description: book response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Book'
        default:
          description: unexpected error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
components:
  schemas:
    Book:
      required:
        - id
        - title
      properties:
        id:
          type: integer
          format: int64
        title:
          type: string
        author:
          type: string
        genre:
          type: string
    NewBook:
      required:
        - title
      properties:
        title:
          type: string
        author:
          type: string
        genre:
          type: string
    Error:
      required:
        - code
        - message
      properties:
        code:
          type: integer
          format: int32
        message:
          type: string
"""
