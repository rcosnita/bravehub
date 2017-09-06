"""Provides the api code for managing projects from the system."""
from flask import request

from src import API_MAJOR_VERSION, ConfigurationApiContainer
from src.app import app

def _get_projects_service():
  return ConfigurationApiContainer.project_service()

@app.route("/v{0}/projects".format(API_MAJOR_VERSION), methods=["GET", "POST"])
def manage_projects():
  """Provides the logic for managing projects."""

  if request.method == "GET":
    return _get_projects_service().list_projects()
  elif request.method == "POST":
    project_data = request.get_json(force=True)
    return _get_projects_service().create_project(project_data)

@app.route("/v{0}/projects/<project_id>".format(API_MAJOR_VERSION),
           methods=["GET", "PUT", "DELETE"])
def manage_project(project_id):
  """Provides the logic for managing an existing project."""

  if request.method == "GET":
    return _get_projects_service().get_project(project_id)
  elif request.method == "PUT":
    return _get_projects_service().update_project(project_id, request.get_json(force=True))
  elif request.method == "DELETE":
    return _get_projects_service().delete_project(project_id)
