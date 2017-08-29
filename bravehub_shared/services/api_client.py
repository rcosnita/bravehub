"""This module provides the generic api client implementation for bravehub core micro services."""

import json
import urllib.parse as parse

class ApiClient(object):
  """The generic class for the api client."""

  DEFAULT_CHARSET = "utf-8"
  API_INTERNAL = "api.internal"

  class ApiClientResponseBody(dict):
    """Provides a simple wrapper which allows us to simulate an object based on the dictionary
    keys."""

    def __init__(self, data):
      super(ApiClient.ApiClientResponseBody, self).__init__()
      self._data = data or {}
      self.update(self._data)

    def __getattr__(self, name):
      value = super(ApiClient.ApiClientResponseBody, self).get(name)

      if isinstance(value, dict):
        return ApiClient.ApiClientResponseBody(value)

      return value

  class ApiClientResponse(object):
    """Provides a simple model returned by api client operations in order to describe
    HTTP responses."""

    def __init__(self, status_code, headers, body):
      self._status_code = status_code
      self._headers = headers or {}
      self._body = body

    @property
    def status_code(self): # pylint: disable=missing-docstring
      return self._status_code

    @property
    def headers(self): # pylint: disable=missing-docstring
      return self._headers

    @property
    def body(self): # pylint: disable=missing-docstring
      return self._body

  def __init__(self, api_name, cluster_suffix, api_port=80, http_client=None):
    self._api_name = api_name
    self._cluster_suffix = cluster_suffix
    self._api_port = api_port
    self._base_url = self._build_base_url()
    self._http_client = http_client

  def get_json(self, api_path, params=None, headers=None):
    """Allows end users to invoke a HTTP get operation using the current api client."""

    req = self._build_request(api_path, params, headers, method="GET")

    with self._http_client.urlopen(req) as resp:
      return self._build_response(resp)

  def post_json(self, api_path, params=None, headers=None, data=None):
    """Allows end users to invoke a HTTP post operation using the current api client."""

    data = json.dumps(data or {})
    req = self._build_request(api_path, params, headers, method="POST", data=data)

    with self._http_client.urlopen(req) as resp:
      return self._build_response(resp)

  def put_json(self, api_path, params=None, headers=None, data=None):
    """Allows end users to invoke a HTTP post operation using the current api client."""

    data = json.dumps(data or {})
    req = self._build_request(api_path, params, headers, method="PUT", data=data)

    with self._http_client.urlopen(req) as resp:
      return self._build_response(resp)

  def delete_json(self, api_path, params=None, headers=None):
    """Allows end users to invoke a HTTP delete operation using the current api client."""

    req = self._build_request(api_path, params, headers, method="DELETE")

    with self._http_client.urlopen(req) as resp:
      return self._build_response(resp)

  def _build_base_url(self):
    return "http://{0}.{1}.{2}:{3}".format(self._api_name, self.API_INTERNAL, self._cluster_suffix,
                                           self._api_port)

  def _read_full_response(self, resp):
    return resp.read().decode(resp.getheader("charset") or self.DEFAULT_CHARSET)

  @property
  def base_url(self): # pylint: disable=missing-docstring
    return self._base_url

  def _build_request(self, api_path, params, headers, method, data=None):
    params = params or {}
    headers = headers or {}

    headers.update({"Content-Type": "application/json"})
    query = parse.urlencode(params)
    url = "{0}{1}".format(self._base_url, api_path)
    if query:
      url = "{0}?{1}".format(url, query)

    return self._http_client.Request(url, headers=headers, method=method, data=data)

  def _transform_headers_tomap(self, headers_lst): # pylint: disable=no-self-use
    return {name: value for name, value in headers_lst or []}

  def _build_response(self, resp):
    return ApiClient.ApiClientResponse(
      status_code=resp.getcode(),
      headers=self._transform_headers_tomap(resp.getheaders()),
      body=ApiClient.ApiClientResponseBody(json.loads(self._read_full_response(resp))))

  def __str__(self):
    return self.base_url
