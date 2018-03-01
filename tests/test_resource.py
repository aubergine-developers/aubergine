"""Test cases for resource module."""
import unittest
from unittest import mock
from falcon import HTTPMethodNotAllowed
from aubergine.resource import Resource

HTTP_METHODS = ['POST', 'GET', 'PUT', 'PATCH', 'OPTIONS', 'HEAD', 'DELETE']

class TestResource(unittest.TestCase):
    """Test case for Resource class."""
    
    def test_doesnt_construct_responders(self):
        """Request should not construct responders for methods not defined in handlers param."""
        for method in HTTP_METHODS:
            handlers = {other_method: mock.Mock() for other_method in HTTP_METHODS
                        if other_method != method}
            res = Resource(handlers, 'some/path/')
            with self.subTest(method=method), self.assertRaises(AttributeError):
                getattr(res, 'on_' + method.lower())(mock.Mock(), mock.Mock())
            
    def test_dispatches_to_correct_handler(self):
        """Request's responders should forward requests to correct handlers."""
        handlers = {method: mock.Mock() for method in HTTP_METHODS}
        resp = mock.Mock()
        req = mock.Mock()
        kwargs = {'arg1': 12, 'arg2': 'someargument'}
        resource = Resource(handlers, '/some/path/')
        for method in HTTP_METHODS:
            getattr(resource, 'on_' + method.lower())(req, resp, **kwargs)
            handlers[method].handle_request.assert_called_once_with(req, resp, **kwargs)

        
    

