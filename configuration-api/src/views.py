"""This module provides all the endpoints and resources supported by the configuration api."""

from bravehub_shared.ioc import ApiClientsContainer
from src.app import app

@app.route("/")
def hello(): # pylint: disable=missing-docstring
  api_client = ApiClientsContainer.logging_api()
  resp = api_client.get_json("/")
  resp_msg = "{0} -----> Api name: {1}: Minor version: {2}"\
    .format(resp.status_code, resp.body.api_name, resp.body.api_version.minor)
  return resp_msg
