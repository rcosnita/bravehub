"""This module provides all the endpoints and resources supported by the configuration api."""

from src import API_FULL_VERSION, API_MAJOR_VERSION
from src.app import app # pylint: disable=cyclic-import

@app.route("/")
def version(): # pylint: disable=missing-docstring
  # api_client = ApiClientsContainer.logging_api()
  # resp = api_client.get_json("/")
  # resp_msg = "{0} -----> Api name: {1}: Minor version: {2}"\
  #   .format(resp.status_code, resp.body.api_name, resp.body.api_version.minor)
  return "Version: {0}".format(API_FULL_VERSION)

import src.apis # pylint: disable=wrong-import-position,unused-import
import src.owners # pylint: disable=wrong-import-position,unused-import
import src.projects # pylint: disable=wrong-import-position,unused-import
