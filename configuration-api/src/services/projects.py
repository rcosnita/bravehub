"""Provides the logic for managing projects."""
import json

from bravehub_shared import CURRENT_USER
from bravehub_shared.exceptions.bravehub_exceptions import \
  BravehubDuplicateEntryException, BravehubNotFoundException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.utils.flask_response_generator import \
  FlaskResponseGenerator, PaginatedResponse

class ProjectService(BravehubService):
  """Provides the validation and persistence logic required for projects management."""

  PROJECTS_TABLE = "projects"
  OWNERS_TABLE = "projectowners"

  def __init__(self, flask_app, conn_pool, charset, id_service): # pylint: disable=too-many-arguments
    super(ProjectService, self).__init__(flask_app, conn_pool, charset)
    self._id_service = id_service

  @FlaskResponseGenerator()
  def list_projects(self):
    """Obtains a list of projects from the system. We do not support filtering, ordering and
    pagination at the moment."""

    projects = []

    owner_id = CURRENT_USER

    with self._conn_pool.connection() as connection:
      owners_tbl = connection.table(self.OWNERS_TABLE)
      owner = owners_tbl.row(bytes(CURRENT_USER, self._charset))

    for key in [k for k in owner.keys() if k.startswith(b"projects:")]:
      data = owner[key]
      project_id = key.replace(b"projects:", b"").decode(self._charset)
      project = json.loads(data.decode(self._charset))
      project["id"] = project_id
      project["owner"] = {"id": owner_id}

      projects.append(project)

    return PaginatedResponse(items=projects)

  @FlaskResponseGenerator()
  def get_project(self, project_id):
    """Fetch an existing project from the database."""
    project = self.get_nondeleted_project(project_id)

    return {
      "id": project_id,
      "name": project[b"attrs:name"].decode(self._charset),
      "description": project[b"attrs:description"].decode(self._charset),
      "domain": project[b"attrs:domain"].decode(self._charset),
      "owner": {
        "id": project[b"owner:id"].decode(self._charset)
      }
    }

  @FlaskResponseGenerator()
  def create_project(self, project_data):
    """Add a new project into the system."""

    owner_id = CURRENT_USER
    project_data = DynamicObject(project_data)

    existing_data = self._get_existing_project(owner_id, project_data.name)

    if existing_data:
      (project_id, existing_project) = existing_data
      existing_project.update({"id": project_id})
      resp_headers = {"Location": self._get_location_header(project_id)}
      raise BravehubDuplicateEntryException(additional_data={"project": existing_project},
                                            headers=resp_headers)

    project_id = self._persist_project_data(project_data, owner_id)
    self._persist_project_to_owner(owner_id, project_id, project_data)

    return None, 201, {"Location": self._get_location_header(project_id)}

  @FlaskResponseGenerator()
  def update_project(self, project_id, project_data): #pylint: disable=missing-docstring
    owner_id = CURRENT_USER
    project_data = DynamicObject(project_data)
    self.get_nondeleted_project(project_id)

    self._persist_project_data(project_data, owner_id, project_id)
    self._persist_project_to_owner(owner_id, project_id, project_data)

  @FlaskResponseGenerator()
  def delete_project(self, project_id): #pylint: disable=missing-docstring
    owner_id = bytes(CURRENT_USER, self._charset)
    self.get_nondeleted_project(project_id)

    with self._conn_pool.connection() as connection:
      owner_proj_col = "projects:{0}".format(project_id)
      connection.table(self.OWNERS_TABLE).delete(owner_id, [bytes(owner_proj_col, self._charset)])
      connection.table(self.PROJECTS_TABLE).put(project_id, {
        b"attrs:state": b"deleted"
      })

  def get_nondeleted_project(self, project_id):
    """Provides the mechanism for obtaining a project uniquely identified by the given identifier.
    In case the project has been deleted, it will not be returned to the client."""
    project = None
    project_id = bytes(project_id, self._charset)

    with self._conn_pool.connection() as connection:
      project = connection.table(self.PROJECTS_TABLE)\
        .scan(row_start=project_id, row_stop=project_id,
              filter="SingleColumnValueFilter('attrs','state',!=,'binary:deleted')",
              limit=1)

    try:
      project_id, project = next(project)
    except StopIteration:
      project = None

    if not project:
      raise BravehubNotFoundException()

    return project

  def _get_existing_project(self, owner_id, project_name):
    with self._conn_pool.connection() as connection:
      projects_tbl = connection.table(self.OWNERS_TABLE)
      project = projects_tbl.row(bytes(owner_id, self._charset))

    for key in [k for k in project.keys() if k.startswith(b"projects:")]:
      project_id = key.decode(self._charset).replace("projects:", "")
      project_data = json.loads(project[key].decode(self._charset))

      if project_data["name"].lower() == project_name.lower():
        return project_id, DynamicObject(project_data)

  def _persist_project_data(self, project_data, owner_id, project_id=None):
    project_id = project_id or self._id_service.generate()

    with self._conn_pool.connection() as connection:
      projects_tbl = connection.table(self.PROJECTS_TABLE)
      projects_tbl.put(bytes(project_id, self._charset), {
        b"attrs:name": bytes(project_data.name, self._charset),
        b"attrs:description": bytes(project_data.description, self._charset),
        b"attrs:domain": bytes(project_data.domain, self._charset),
        b"owner:id": bytes(owner_id, self._charset)
      })

    return project_id

  def _persist_project_to_owner(self, owner_id, project_id, project_data):
    with self._conn_pool.connection() as connection:
      owners_tbl = connection.table(self.OWNERS_TABLE)
      new_project = {
        bytes("projects:{0}".format(project_id), self._charset): \
          bytes(json.dumps(project_data), self._charset)
      }
      owners_tbl.put(bytes(owner_id, self._charset), new_project)

  def _get_location_header(self, project_id): #pylint: disable=no-self-use
    from src import API_MAJOR_VERSION
    return "/v{0}/{1}/{2}".format(API_MAJOR_VERSION, "projects", project_id)
