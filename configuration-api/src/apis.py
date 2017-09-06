"""Provides the api code for managing project apis from the system."""
import json

from flask import request

from bravehub_shared.exceptions.error_codes import ErrorCodes

from src import API_MAJOR_VERSION, ConfigurationApiContainer
from src.app import app


CONFIGASSET_CONTENT_TYPE = "application/vnd.bravehub.configurationasset-binary"
DROPLET_CONTENT_TYPE = "application/vnd.bravehub.droplet-binary"

@app.route("/v{0}/projects/<project_id>/apis".format(API_MAJOR_VERSION), methods=["GET", "POST"])
def manage_apis(project_id):
  """Provides the logic for managing apis belonging to a project."""

  if request.method == "GET":
    return _get_apis_service().list_apis(project_id)
  elif request.method == "POST":
    return _get_apis_service().create_api(project_id, request.get_json(force=True))

@app.route("/v{0}/projects/<project_id>/apis/<api_id>".format(API_MAJOR_VERSION),
           methods=["GET", "PUT", "DELETE"])
def manage_api(project_id, api_id):
  """Provides the logic for managing an existing api belonging to a project."""

  if request.method == "GET":
    return _get_apis_service().get_api(project_id, api_id)
  elif request.method == "PUT":
    return _get_apis_service().update_api(project_id, api_id, request.get_json(force=True))
  elif request.method == "DELETE":
    return _get_apis_service().delete_api(project_id, api_id)

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>".format(API_MAJOR_VERSION),
           methods=["GET", "PUT"])
def manage_build(project_id, api_id, build):
  """Provides the algorithm for uploading content belonging to a build. For the moment, we only
  support the droplet upload."""

  content_type_err = _validate_content_type(request, DROPLET_CONTENT_TYPE)
  if content_type_err:
    return content_type_err

  if request.method == "PUT":
    return _get_binaries_service().save_droplet(project_id=project_id, api_id=api_id, build=build,
                                                content=request.stream)
  elif request.method == "GET":
    return _get_binaries_service().download_droplet(project_id=project_id, api_id=api_id,
                                                    build=build)

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/configassets"\
           .format(API_MAJOR_VERSION), methods=["POST"])
def manage_config_assets(project_id, api_id, build):
  """Provides the logic for creating a new configuration asset for the specified build."""
  content_type_err = _validate_content_type(request, CONFIGASSET_CONTENT_TYPE)
  if content_type_err:
    return content_type_err

  mount_path = _get_mount_path(request)
  return _get_binaries_service().save_configasset(project_id=project_id, api_id=api_id,
                                                  build=build,
                                                  mount_path=mount_path,
                                                  content=request.stream)

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/configassets/<asset_id>"\
           .format(API_MAJOR_VERSION), methods=["GET", "PUT"])
def manage_config_asset(project_id, api_id, build, asset_id):
  """Provides the logic for managing an existing configuration asset identified by the given asset_id."""

  content_type_err = _validate_content_type(request, CONFIGASSET_CONTENT_TYPE)
  if content_type_err:
    return content_type_err

  if request.method == "PUT":
    mount_path = _get_mount_path(request)
    return _get_binaries_service().save_configasset(project_id=project_id, api_id=api_id,
                                                    build=build, asset_id=asset_id,
                                                    mount_path=mount_path,
                                                    content=request.stream)
  elif request.method == "GET":
    return _get_binaries_service().download_configasset(project_id=project_id, api_id=api_id,
                                                        build=build, asset_id=asset_id)

def _get_apis_service():
  return ConfigurationApiContainer.api_service()

def _get_binaries_service():
  return ConfigurationApiContainer.config_binaries_service()

def _get_mount_path(req):
  return req.headers.get("X-ConfigAsset-MountPath")

def _validate_content_type(req, content_type):
  if not req.headers.get("Content-Type") == content_type:
    error = {
      "errorId": ErrorCodes.RESOURCE_NOT_IMPLEMENTED_ERROR["id"],
      "errorCode": ErrorCodes.RESOURCE_NOT_IMPLEMENTED_ERROR["code"],
      "description": "Only {0} content type is supported.".format(content_type)
    }

    return app.response_class(response=json.dumps(error),
                              status=501,
                              mimetype="application/json")
