"""Provides the api code for managing project apis from the system."""
from flask import request

from src import API_MAJOR_VERSION, ConfigurationApiContainer
from src.app import app

def _get_apis_service():
  return ConfigurationApiContainer.api_service()

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

  return "Managing api {0} for project {1}".format(api_id, project_id)
