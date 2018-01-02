"""Provides the unit tests for flask response generator decorator. These tests are meant
to freeze the contract provided by this decorator."""
import json
import unittest
from unittest.mock import Mock

from bravehub_shared.exceptions.bravehub_exceptions import BravehubPlatformException
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator

class MockCustomException(BravehubPlatformException): # pylint: disable=missing-docstring
  @property
  def status_code(self):
    return 599

  @property
  def body(self):
    return {
      "errorId": "CUSTOM.0",
      "errorCode": "CUSTOM.unknown",
      "errorDescription": "Hahahaha"
    }

class MockResponseClass(object): # pylint: disable=too-few-public-methods,missing-docstring
  def __init__(self, response, status, mimetype, headers=None):
    self.response = response
    self.status = status
    self.mimetype = mimetype
    self.headers = headers

class FlaskResponseGeneratorTests(unittest.TestCase): # pylint: disable=missing-docstring
  MIMETYPE_JSON = "application/json"

  def setUp(self):
    self._flask_app = Mock()
    self._flask_app.response_class = MockResponseClass

  @property
  def flask_app(self): # pylint: disable=missing-docstring
    return self._flask_app

  def test_body_response(self): # pylint: disable=missing-docstring
    expected_body = {"a": "B"}
    result = self._return_body_response(expected_body)

    self._assert_response_headers(result, 200, self.MIMETYPE_JSON)
    self.assertEqual(json.loads(result.response), expected_body) # pylint: disable=no-member

  def test_emptybody_response(self): # pylint: disable=missing-docstring
    result = self._return_body_response(None)

    self._assert_response_headers(result, 204, self.MIMETYPE_JSON)
    self.assertEqual(result.response, "") # pylint: disable=no-member

  def test_201_headers_response(self): # pylint: disable=missing-docstring
    expected_location = "/new/resource/location"
    result = self._return_201_body(expected_location, None)

    self._assert_response_headers(result, 201, self.MIMETYPE_JSON)
    self.assertEqual(result.headers, {"Location": expected_location}) # pylint: disable=no-member

  def test_generic_error_response(self): # pylint: disable=missing-docstring
    expected_err = Exception()
    result = self._return_unhandled_error(expected_err)

    self._assert_response_headers(result, 500, self.MIMETYPE_JSON)
    self._assert_error_body(result, BravehubPlatformException())

  def test_error_debug_response(self): # pylint: disable=missing-docstring
    expected_err = Exception()

    try:
      self._return_debug_error(expected_err)
      self.assertTrue(False) # pylint: disable=redundant-unittest-assert
    except Exception as ex: # pylint: disable=broad-except
      self.assertEqual(expected_err, ex)

  def test_error_headers_response(self): # pylint: disable=missing-docstring
    expected_err = MockCustomException(headers={"X-CustomHeader-1": "aaabbb"})

    result = self._return_unhandled_error(expected_err)
    self._assert_response_headers(result, expected_err.status_code, self.MIMETYPE_JSON)
    self._assert_error_body(result, expected_err)
    self.assertEqual(result.headers["X-CustomHeader-1"], "aaabbb")

  def test_platform_error_response(self): # pylint: disable=missing-docstring
    expected_err = MockCustomException()

    result = self._return_unhandled_error(expected_err)
    self._assert_response_headers(result, expected_err.status_code, self.MIMETYPE_JSON)
    self._assert_error_body(result, expected_err)

  def _assert_response_headers(self, result, expected_status, expected_mimetype):
    self.assertIsNotNone(result)
    self.assertEqual(result.status, expected_status) # pylint: disable=no-member
    self.assertEqual(result.mimetype, expected_mimetype) # pylint: disable=no-member

  def _assert_error_body(self, result, expected_ex):
    self.assertEqual(json.loads(result.response), expected_ex.body)

  @FlaskResponseGenerator()
  def _return_body_response(self, body): # pylint: disable=no-self-use
    return body

  @FlaskResponseGenerator(app_attr="_flask_app")
  def _return_unhandled_error(self, error): # pylint: disable=no-self-use
    raise error

  @FlaskResponseGenerator(app_attr="_flask_app", is_debug=True)
  def _return_debug_error(self, error): # pylint: disable=no-self-use
    raise error

  @FlaskResponseGenerator()
  def _return_201_body(self, location, body): # pylint: disable=no-self-use
    return (body, 201, {"Location": location})
