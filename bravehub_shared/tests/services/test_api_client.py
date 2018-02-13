"""Provides the unit tests for the api client implementation."""

import json
import unittest
from unittest.mock import Mock, MagicMock
import urllib.parse as parse

from bravehub_shared.services.api_client import ApiClient

class ApiClientTests(unittest.TestCase): # pylint: disable=missing-docstring
  CLUSTER_SUFFIX = "cluster.suffix.com"

  def setUp(self): # pylint: disable=missing-docstring
    self._api_name = "configuration-api"
    self._api_port = "9000"
    self._base_url = "http://{0}.api.internal.{1}:{2}".format(self._api_name, self.CLUSTER_SUFFIX,
                                                              self._api_port)
    self._http_client_inst = Mock()
    self._http_client = Mock()
    self._http_client.Request = Mock(return_value=self._http_client_inst)
    self._api_client = ApiClient(self._api_name, self.CLUSTER_SUFFIX, self._api_port,
                                 self._http_client)

  def test_base_url_ok(self): # pylint: disable=missing-docstring
    self.assertEqual(self._api_client.base_url, self._base_url)

  def test_get_json(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    expected_body = {"data": "works as expected"}

    self._test_http_json(path=path, req_headers={}, params=params, expected_body=expected_body,
                         resp_headers={})

  def test_get_json_contentheader(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_body = {"data": "works as expected"}

    self._test_http_json(path=path, req_headers={"Content-Type": "custom/headers"},
                         expected_body=expected_body, resp_headers={})

  def test_get_json_empty_body(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"

    self._test_http_json(path=path, req_headers={}, expected_body=None, resp_headers={})

  def test_get_json_response_headers(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    resp_headers = {
      "charset": "utf-16",
      "X-CustomHeader": "abcd"
    }

    self._test_http_json(path=path, req_headers={}, expected_body=None, resp_headers=resp_headers)

  def test_get_json_unexpected_error(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_ex = Exception("Unexpected error")

    self._http_client.urlopen = Mock(side_effect=expected_ex)

    try:
      self._api_client.get_json(path)
      self.assertTrue(False) # pylint: disable=redundant-unittest-assert
    except Exception as ex: # pylint: disable=broad-except
      self.assertTrue(ex == expected_ex)

  def test_post_json(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    req_body = {"data": "Everything is ok"}
    expected_body = None
    resp_headers = {"Location": "/api/v1/configurations/1234"}

    self._test_http_json(path=path, req_headers={}, params=params, req_body=req_body,
                         method="POST", expected_body=expected_body, resp_headers=resp_headers)

  def test_post_json_no_body(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    req_body = None
    expected_body = None
    resp_headers = {"Location": "/api/v1/configurations/1234"}

    self._test_http_json(path=path, req_headers={}, params=params, req_body=req_body,
                         method="POST", expected_body=expected_body, resp_headers=resp_headers)

  def test_post_json_content(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    req_body = None
    expected_body = None
    req_headers = {"Content-Type": "unknown/content-type"}
    resp_headers = {"Location": "/api/v1/configurations/1234"}

    self._test_http_json(path=path, req_headers=req_headers, params=params, req_body=req_body,
                         method="POST", expected_body=expected_body, resp_headers=resp_headers)

  def test_post_json_unexpected_error(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_ex = Exception("Unexpected error")

    self._http_client.urlopen = Mock(side_effect=expected_ex)

    try:
      self._api_client.post_json(path)
      self.assertTrue(False) # pylint: disable=redundant-unittest-assert
    except Exception as ex: # pylint: disable=broad-except
      self.assertTrue(ex == expected_ex)

  def test_put_json(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    req_body = {"data": "Everything is ok"}
    expected_body = None
    resp_headers = {"X-Custom-Header": "Works just fine"}

    self._test_http_json(path=path, req_headers={}, params=params, req_body=req_body,
                         method="PUT", expected_body=expected_body, resp_headers=resp_headers)

  def test_put_json_no_body(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    expected_body = None
    resp_headers = {}

    self._test_http_json(path=path, req_headers={}, params=params, req_body=None,
                         method="PUT", expected_body=expected_body, resp_headers=resp_headers)

  def test_put_json_content(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    req_headers = {"Content-Type": "unknown/content-type"}

    self._test_http_json(path=path, req_headers=req_headers, params=params, req_body=None,
                         method="PUT", expected_body=None, resp_headers={})

  def test_put_json_unexpected_error(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_ex = Exception("Unexpected error")

    self._http_client.urlopen = Mock(side_effect=expected_ex)

    try:
      self._api_client.put_json(path)
      self.assertTrue(False) # pylint: disable=redundant-unittest-assert
    except Exception as ex: # pylint: disable=broad-except
      self.assertTrue(ex == expected_ex)

  def test_delete_json(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    params = {"a": "b"}
    expected_body = {"data": "works as expected"}

    self._test_http_json(path=path, req_headers={}, params=params, method="DELETE",
                         expected_body=expected_body, resp_headers={})

  def test_delete_json_contentheader(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_body = {"data": "works as expected"}

    self._test_http_json(path=path, req_headers={"Content-Type": "custom/headers"}, method="DELETE",
                         expected_body=expected_body, resp_headers={})

  def test_delete_json_empty_body(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"

    self._test_http_json(path=path, req_headers={}, expected_body={}, resp_headers={},
                         method="DELETE")

  def test_delete_json_resp_headers(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    resp_headers = {
      "charset": "utf-16",
      "X-CustomHeader": "abcd"
    }

    self._test_http_json(path=path, req_headers={}, expected_body={},
                         resp_headers=resp_headers, method="DELETE")

  def test_delete_json_error(self): # pylint: disable=missing-docstring
    path = "/api/v1/configurations"
    expected_ex = Exception("Unexpected error")

    self._http_client.urlopen = Mock(side_effect=expected_ex)

    try:
      self._api_client.delete_json(path)
      self.assertTrue(False) # pylint: disable=redundant-unittest-assert
    except Exception as ex: # pylint: disable=broad-except
      self.assertTrue(ex == expected_ex)

  def _test_http_json(self, path=None, params=None, req_headers=None, req_body=None, # pylint: disable=too-many-arguments
                      expected_body=None, method="GET", resp_headers=None, resp_status_code=200):
    (assert_response_calls, expected_resp) =\
      self._build_mock_response(resp_status_code, resp_headers, json.dumps(expected_body))

    assert_request_calls = self._build_mock_request(path=path, params=params, req_body=req_body,
                                                    method=method, expected_resp=expected_resp)

    result = None

    if method == "GET":
      result = self._api_client.get_json(path, params=params, headers=req_headers)
    elif method == "POST":
      result = self._api_client.post_json(path, params=params, headers=req_headers, data=req_body)
    elif method == "PUT":
      result = self._api_client.put_json(path, params=params, headers=req_headers, data=req_body)
    elif method == "DELETE":
      result = self._api_client.delete_json(path, params=params, headers=req_headers)

    assert_request_calls()
    assert_response_calls()

    self.assertIsNotNone(result)
    self.assertEqual(result.status_code, resp_status_code)
    self.assertEqual(result.headers, resp_headers)
    self.assertEqual(result.body, expected_body or {})

  def _build_mock_request(self, path, params, expected_resp, req_body=None, method="GET"):
    self._http_client.urlopen = Mock(return_value=expected_resp)

    def _assert_request_calls():
      expected_url = "{0}{1}".format(self._base_url, path)
      if params:
        expected_url = "{0}?{1}".format(expected_url, parse.urlencode(params))

      expected_req_body = req_body
      if method in ["PUT", "POST"]:
        expected_req_body = json.dumps(req_body or {}).encode("UTF-8")

      self._http_client.Request.assert_called_with(expected_url,
                                                   headers={"Content-Type": "application/json"},
                                                   method=method,
                                                   data=expected_req_body)
      self._http_client.urlopen.assert_called_with(self._http_client_inst)

    return _assert_request_calls

  def _build_mock_response(self, status_code, headers, body): # pylint: disable=no-self-use
    response = MagicMock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock()
    response.getcode = Mock(return_value=status_code)
    response.getheader = headers.get
    response.getheaders = Mock(return_value=[(name, headers.get(name)) for name in headers])
    response.read = Mock(return_value=response)
    response.decode = Mock(return_value=body)

    def _assert_response_calls():
      response.decode.assert_called_with(headers.get("charset") or "utf-8")
      response.getheaders.assert_called()

    return (_assert_response_calls, response)
