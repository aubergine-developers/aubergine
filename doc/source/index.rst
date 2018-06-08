.. aubergine documentation master file, created by
   sphinx-quickstart on Sun May 20 09:04:49 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aubergine documentation
=====================================

**aubergine** is a library that helps you in effortlessly creating REST API using
API-first approach.

Creating an API in **aubergine** simple and requires only the following steps:
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

2. Implement operations that you declared in your specification. Place `hello_world`` module with the following contents in an importable directory.

.. code:: python

   def hello(who):
       """Handles v1/rest/hello"""
       return {'message': 'Hello {}!'.format(who)}


3. Tell aubergine to run your app. Create a ``hello_app.py`` with the following contents:

.. code:: python

   from aubergine import Aubergine

   app = Aubergine.from_file('hello_world.yml')
   api = app.build_api()

4. Your app is ready to go. You can run it with any WSGI server like so:

.. code:: bash

   gunicorn hello_app:api


Test it by navigating to ``http://localhost:8000/v1/rest/hello?who=World``


.. toctree::
   :caption: User documentation
   :maxdepth: 4

   userdoc/userdoc.rst

.. toctree::
   :caption: Technical reference
   :maxdepth: 4

   reference/aubergine.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
