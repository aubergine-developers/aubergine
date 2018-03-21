"""Test cases for request handlers."""
import unittest
from unittest import mock
from aubergine.decoders import ParameterValidationError
from aubergine.handlers import RequestHandler


class TestRequestHandler(unittest.TestCase):
    """Test case for RequestHandler class."""

    body_dec = mock.Mock()
    path_dec = mock.Mock()
    get_dec = mock.Mock()
    err_dec = mock.Mock()

    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.err_dec.decode.side_effect = ParameterValidationError(['error msg1', 'error mesg2'])
        cls.body_dec.decode.return_value = {'name': 'John', 'last_name': 'Doe'}
        cls.get_dec.decode.return_value = 20
        cls.path_dec.decode.return_value = 'johndoe'

    def setUp(self):
        """Set up test."""
        for _mock in (self.body_dec, self.path_dec, self.get_dec, self.err_dec):
            _mock.reset_mock()

    def test_get_parameter_dict(self):
        """RequestHandler should correctly extract parameters using its decoders."""
        param_decoders = {'uname': self.path_dec, 'limit': self.get_dec}
        operation = mock.Mock()
        req = mock.Mock()
        kwargs = {'uname': '_johndoe_'}

        handler = RequestHandler(operation, self.body_dec, param_decoders)
        params = handler.get_parameter_dict(req, **kwargs)

        exp_params = {
            'uname': 'johndoe',
            'limit': 20
        }

        self.assertEqual(exp_params, params)
        self.path_dec.decode.assert_called_once_with(req, **kwargs)
        self.get_dec.decode.assert_called_once_with(req, **kwargs)
