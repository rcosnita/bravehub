"""Provides the service which manages project apis."""
import json

from bravehub_shared.exceptions.bravehub_exceptions import \
  BravehubDuplicateEntryException, BravehubNotFoundException, BravehubNotImplementedException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator

class ProjectApiService(BravehubService):
  """Provides the services which offers all management methods for apis."""

  PROJECTS_TABLE = "projects"
  APIS_TABLE = "apis"

  def __init__(self, flask_app, conn_pool, charset, project_service, id_service): # pylint: disable=too-many-arguments
    super(ProjectApiService, self).__init__(flask_app, conn_pool, charset)
    self._project_service = project_service
    self._id_service = id_service

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

    project = self._project_service.get_nondeleted_project(project_id)

    api_data = DynamicObject(api_data)
    api_path = api_data.path

    self._validate_api_notfound(project_id, project, api_path)

    api_id = self._id_service.generate_bytes()
    build_data = api_data.build

    build_attrs = {
      "id": self._id_service.generate(),
      "description": build_data.description
    }
    build_config = build_data.configuration
    secrets_data = build_config.secrets
    for secret in secrets_data:
      secret.update({"id": self._id_service.generate()})

    environment_data = build_config.environment
    for env in secrets_data:
      env.update({"id": self._id_service.generate()})

    with self._conn_pool.connection() as connection:
      apis_tbl = connection.table("apis")
      apis_tbl.put(api_id, {
        b"project:id": bytes(project_id, self._charset),
        b"project:name": project[b"attrs:name"],
        b"attrs:path": bytes(api_path, self._charset),
        b"builds:counter": b"1",
        b"builds:1-attrs": bytes(json.dumps(build_attrs), self._charset),
        b"builds:1-secrets": bytes(json.dumps(secrets_data), self._charset),
        b"builds:1-env": bytes(json.dumps(environment_data), self._charset)
      })

      projects_tbl = connection.table("projects")
      projects_tbl.put(bytes(project_id, self._charset), {
        "apis:{0}".format(api_id.decode(self._charset)): bytes(json.dumps({
          "path": api_data.path
        }), self._charset)
      })

    return None, 201, {"Location": self._get_api_location(project_id, api_id.decode(self._charset))}

  @FlaskResponseGenerator()
  def update_api(self, project_id, api_id, api_data):
    """Provides the algorithm for updating an existing api definition."""

    project = self._project_service.get_nondeleted_project(project_id)
    api_data = DynamicObject(api_data)
    api_path = api_data.path

    self._validate_api_notfound(project_id, project, api_path)

    api_id = bytes(api_id, self._charset)
    api = self.get_nondeleted_api(bytes(project_id, self._charset), api_id)

    builds_data = api_data.builds

    with self._conn_pool.connection() as connection:
      apis_tbl = connection.table("apis")

      for build_data in builds_data:
        build_data = DynamicObject(build_data)
        build_num = build_data.build
        existing_build = self._get_build_cellvalue(api, build_num, "attrs")
        build_id = None
        if not existing_build:
          build_id = self._id_service.generate()

        build_attrs = {
          "id": build_id or json.loads(existing_build)["id"],
          "description": build_data.description
        }

        build_config = build_data.configuration
        secrets_data = build_config.secrets
        environment_data = build_config.environment

        apis_tbl.put(api_id, {
          b"project:id": bytes(project_id, self._charset),
          b"project:name": project[b"attrs:name"],
          b"builds:counter": bytes(str(len(builds_data)), self._charset),
          b"attrs:path": bytes(api_path, self._charset),
          self._get_build_cellname(build_num, "attrs"): \
            bytes(json.dumps(build_attrs), self._charset),
          self._get_build_cellname(build_num, "secrets"): \
            bytes(json.dumps(secrets_data), self._charset),
          self._get_build_cellname(build_num, "env"): \
            bytes(json.dumps(environment_data), self._charset)
        })

    return None, 204, {}

  @FlaskResponseGenerator()
  def get_api(self, project_id, api_id, build_num=None, asset_id=None):
    """Fetches an existing API from the database (if any is available)."""

    api = self.get_nondeleted_api(bytes(project_id, self._charset), bytes(api_id, self._charset))

    builds = []
    builds_counter = int(api[b"builds:counter"].decode(self._charset))

    for idx in range(1, builds_counter + 1):
      build_attrs = DynamicObject(json.loads(self._get_build_cellvalue(api, idx, "attrs")))
      
      secrets_data = json.loads(self._get_build_cellvalue(api, idx, "secrets"))
      for secret in secrets_data:
        secret.pop("value", None)

      assets = []
      for key in [k for k in api.keys() if k.startswith(self._get_build_cellname(idx, "assets-"))]:
        key = key.decode(self._charset)
        curr_asset_id = key.replace("builds:{0}-assets-".format(idx), "")
        asset_data = DynamicObject(json.loads(self._get_build_cellvalue(api, idx,
                                              "assets-{0}".format(curr_asset_id))))
        assets.append({
          "id": curr_asset_id,
          "downloadPath": asset_data.download_path,
          "mountPath": asset_data.mount_path,
          "fileSize": asset_data.file_size,
          "md5sum": asset_data.md5sum
        })

      droplet_data = self._get_build_cellvalue(api, idx, "droplet")
      droplet = None

      if droplet_data:
        droplet_data = DynamicObject(json.loads(droplet_data))
        droplet = {
          "id": droplet_data.id,
          "downloadPath": droplet_data.download_path,
          "md5sum": droplet_data.md5sum,
          "fileSize": droplet_data.file_size
        }

      builds.append({
        "id": build_attrs.id,
        "build": idx, 
        "description": build_attrs.description,
        "configuration": {
          "secrets": secrets_data,
          "environment": json.loads(self._get_build_cellvalue(api, idx, "env")),
          "assets": assets,
          "droplet": droplet
        }
      })

    if build_num:
      curr_build = builds[build_num - 1]
      if not asset_id:
        return curr_build

      curr_build = DynamicObject(curr_build)
      asset = [asset for asset in curr_build.configuration.assets if asset["id"] == asset_id]
      return asset[0]

    builds.sort(key=lambda item: item["build"], reverse=True)

    return {
      "id": api_id,
      "path": api[b"attrs:path"].decode(self._charset),
      "project": {
        "id": project_id,
        "name": api[b"project:name"].decode(self._charset)
      },
      "builds": builds
    }

  @FlaskResponseGenerator()
  def delete_api(self, project_id, api_id):
    """Provides the logic for deleting an existing API."""

    self._project_service.get_nondeleted_project(project_id)

    proj_api_col = "apis:{0}".format(api_id)
    project_id = bytes(project_id, self._charset)
    api_id = bytes(api_id, self._charset)

    self.get_nondeleted_api(project_id, api_id)

    with self._conn_pool.connection() as connection:
      api_tbl = connection.table("apis")
      projects_tbl = connection.table("projects")

      projects_tbl.delete(project_id, [bytes(proj_api_col, self._charset)])
      api_tbl.put(api_id, {
        b"attrs:state": b"deleted"
      })

  def get_nondeleted_api(self, project_id, api_id):
    with self._conn_pool.connection() as connection:
      apis_tbl = connection.table("apis")
      api = apis_tbl.row(api_id)

    if not api or api[b"project:id"] != project_id or \
      (b"attrs:state" in api.keys() and api[b"attrs:state"] == b"deleted"):
      raise BravehubNotFoundException()

    return api

  def _get_build_cellname(self, build_num, cell_name):
    return bytes("builds:{0}-{1}".format(build_num, cell_name), self._charset)

  def _get_build_cellvalue(self, api, build_num, cell_name):
    build_cell_name = self._get_build_cellname(build_num, cell_name)

    try:
      return api[build_cell_name].decode(self._charset)
    except KeyError:
      None

  def _get_api_location(self, project_id, api_id): # pylint: disable=no-self-use
    from src import API_MAJOR_VERSION
    return "/v{0}/projects/{1}/apis/{2}".format(API_MAJOR_VERSION, project_id, api_id)

  def _get_api_bypath(self, project, api_path):
    for key in [k for k in project.keys() if k.startswith(b"apis:")]:
      api_data = DynamicObject(json.loads(project[key].decode(self._charset)))
      api_id = key.decode(self._charset).replace("apis:", "")

      if api_data.path == api_path:
        api_data.update({"id": api_id})
        return api_data

  def _validate_api_notfound(self, project_id, project, api_path):
    existing_api = self._get_api_bypath(project, api_path)
    if existing_api:
      resp_headers = {"Location": self._get_api_location(project_id, existing_api.id)}
      raise BravehubDuplicateEntryException(additional_data={"api": existing_api.id},
                                            headers=resp_headers)
