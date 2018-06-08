aubergine: create REST APIs using API-first approach.
==========================================================================

|License: MIT|

**aubergine** is a library that helps you effortlessly create REST API using
API-first approach.

Creating an API in **aubergine** is simple and requires only the following steps:

1. Create your OpenAPI 3 specification file, with ``operationId`` set to the callable of your choice.

.. code:: yaml

   openapi: "3.0.0"
   servers:
     - url: /v1/rest
   info:
     version: 1.0.0
     title: Hello World
     description: My first api.
   paths:
     /hello:
       get:
	 operationId: hello_world.hello
	 parameters:
	   - who: who
	     in: query
	     description: who to great
	     required: true
	     schema:
	       type: string
	 responses:
	   '200':
	     description: Greeting dedicated to given name.
	     content:
	       application/json:
		 schema:
		     $ref: '#/components/schemas/Greeting'
   components:
     schemas:
       Greeting:
	 required:
	   - message
	 properties:
	   message:
	     type: string

2. Implement operations that you declared in your specification. Place ``hello_world`` module with the following content in an importable directory.

.. code:: python

   def hello(who):
       """Handles v1/rest/hello"""
       return {'message': 'Hello {}!'.format(who)}


3. Tell aubergine to create an app for you. Create a ``hello_app.py`` with the following contents:

.. code:: python

   from aubergine import Aubergine

   app = Aubergine.from_file('hello_world.yml')
   api = app.build_api()

4. Your app is ready to go. You can run it with any WSGI server like so:

.. code:: bash

   gunicorn hello_app:api


Test it by navigating to ``http://localhost:8000/v1/rest/hello?who=World``

.. |License: MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
