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

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>".format(API_MAJOR_VERSION),
           methods=["GET", "PUT"])
def manage_build(project_id, api_id, build):
  """Provides the logic for managing an existing build identified by build number."""

  return "Managing build {0}".format(build)

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/configassets"\
           .format(API_MAJOR_VERSION), methods=["POST"])
def manage_config_assets(project_id, api_id, build):
  """Provides the logic for managing an existing build identified by build number."""

  return "Managing configuration assets for build {0}".format(build)

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/configassets/<asset_id>"\
           .format(API_MAJOR_VERSION), methods=["GET"])
def manage_config_asset(project_id, api_id, build, asset_id):
  """Provides the logic for managing an existing build identified by build number."""

  return "Managing configuration asset {0}".format(asset_id)
