"""Provides the service which manages project apis."""
import json

from bravehub_shared.exceptions.bravehub_exceptions import BravehubNotImplementedException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator

class ProjectApiService(BravehubService):
  """Provides the services which offers all management methods for apis."""

  PROJECTS_TABLE = "projects"
  APIS_TABLE = "apis"

  def __init__(self, flask_app, conn_pool, charset, project_service):
    super(ProjectApiService, self).__init__(flask_app, conn_pool, charset)
    self._project_service = project_service

  @FlaskResponseGenerator()
  def list_apis(self, project_id):
    """Retrieve all defined APIs for the given project."""

    project = self._project_service.get_nondeleted_project(project_id)
    project_attrs = {
      "id": project_id,
      "name": project[b"attrs:name"].decode(self._charset)
    }
    apis = []

    for key in [k for k in project.keys() if k.startswith(b"apis:")]:
      apis.append(json.loads(project[key]))
      apis[-1]["id"] = key.decode(self._charset).replace("apis:", "")
      apis[-1].update({"project": project_attrs})

    return {
      "items": apis,
      "startRecord": None,
      "endRecord": None,
      "previous": None,
      "next": None,
      "limit": None
    }

  @FlaskResponseGenerator()
  def create_api(self, project_id, api_data):
    """Creates a new API and associates it with the given project."""

    raise BravehubNotImplementedException()
