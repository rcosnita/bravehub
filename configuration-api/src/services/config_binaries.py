"""Provides the implementation of a service which can correctly store the configuration
binary content for assets and droplets."""

import json
import os

from bravehub_shared.exceptions.bravehub_exceptions import \
  BravehubDuplicateEntryException, BravehubNotFoundException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager

class ConfigBinariesService(BravehubService):
  """Provides the logic for managing configuration binary content and its metadata."""

  BINARIES_ROOT_FOLDER = "/projects"

  def __init__(self, flask_app, conn_pool, charset, file_system, # pylint: disable=too-many-arguments
               project_service, api_service, id_service):
    super(ConfigBinariesService, self).__init__(flask_app, conn_pool, charset)
    self._file_system = file_system
    self._project_service = project_service
    self._api_service = api_service
    self._id_service = id_service

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def save_droplet(self, project_id, api_id, build, content, hbase_manager):
    """Stores the given binary content and its generated metadata."""

    self._validate_has_build(project_id, api_id, build)

    droplet_id = self._id_service.generate()
    droplet_name = "{0}.tar.gz".format(build)
    droplet_path = self._get_binary_path(project_id, api_id, build, "droplets")
    droplet_full_path = os.path.join(droplet_path, droplet_name)

    self._file_system.store(file_name=droplet_name, stream=content, folder_path=droplet_path)

    conn = hbase_manager.connection
    apis_tbl = conn.table("apis")
    apis_tbl.put(bytes(api_id, self._charset), {
      bytes("builds:{0}-droplet".format(build), self._charset): bytes(json.dumps({
        "id": droplet_id,
        "download_path": droplet_full_path,
        "md5sum": self._file_system.crc(droplet_full_path),
        "file_size": self._file_system.size(droplet_full_path)
      }), self._charset)
    })

    return self._api_service.get_api(project_id, api_id, int(build))

  @FlaskResponseGenerator()
  def download_droplet(self, project_id, api_id, build):
    """Downloads the droplet for the specified build."""

    (project, api) = self._validate_has_build(project_id, api_id, build) #pylint: disable=unused-variable

    droplet_cell = "builds:{0}-droplet".format(build)
    droplet = DynamicObject(json.loads(api[bytes(droplet_cell, self._charset)]\
                                .decode(self._charset)))

    return self._file_system.get(file_path=droplet.download_path)

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def save_configasset(self, project_id, api_id, build, mount_path, content, asset_id=None, #pylint: disable=too-many-arguments,too-many-locals
                       hbase_manager=None):
    """Save the given configuration asset."""

    (project, api, asset) = self._validate_has_asset(project_id, api_id, build, asset_id) #pylint: disable=unused-variable

    if not asset_id:
      self._enforce_mount_path_unicity(project_id, api_id, api, build, mount_path)
      asset_id = self._id_service.generate()

    asset_cell = bytes("builds:{0}-assets-{1}".format(build, asset_id), self._charset)

    if asset:
      self._file_system.delete(asset.download_path)

    (folder_path, file_name) = self._file_system.split_file_path(mount_path)
    folder_path = os.path.join("/configs", "assets", asset_id, folder_path[1:])
    folder_path = self._get_binary_path(project_id, api_id, build, folder_path[1:])
    self._file_system.store(file_name=file_name, stream=content, folder_path=folder_path)

    download_path = os.path.join(folder_path, file_name)

    conn = hbase_manager.connection
    apis_tbl = conn.table("apis")
    apis_tbl.put(bytes(api_id, self._charset), {
      bytes(asset_cell): bytes(json.dumps({
        "download_path": download_path,
        "mount_path": mount_path,
        "file_size": self._file_system.size(download_path),
        "md5sum": self._file_system.crc(download_path)
      }), self._charset)
    })

    location = self._get_configasset_location(project_id, api_id, build, asset_id)
    return None, 201, {"Location": location}

  @FlaskResponseGenerator()
  def download_configasset(self, project_id, api_id, build, asset_id):
    """Downloads the asset content if available."""

    (project, api, asset) = self._validate_has_asset(project_id, api_id, build, asset_id) #pylint: disable=unused-variable
    return self._file_system.get(file_path=asset.download_path)

  def _get_build(self, api, build):
    return api.get(bytes("builds:{0}-attrs".format(build), self._charset))

  def _has_build(self, api, build):
    return self._get_build(api, build) is not None

  def _enforce_mount_path_unicity(self, project_id, api_id, api, build, mount_path):
    build_cell = bytes("builds:{0}-assets-".format(build), self._charset)
    for key in [k for k in api.keys() if k.startswith(build_cell)]:
      asset = DynamicObject(json.loads(api[key].decode(self._charset)))
      asset_id = key.replace(build_cell, b"").decode(self._charset)
      if asset.mount_path == mount_path:
        resp_headers = {"Location": self._get_configasset_location(project_id, api_id, build,
                                                                   asset_id)}
        raise BravehubDuplicateEntryException(additional_data={"asset": asset_id},
                                              headers=resp_headers)

  def _validate_has_build(self, project_id, api_id, build):
    project = self._project_service.get_nondeleted_project(project_id)
    api = self._api_service.get_nondeleted_api(bytes(project_id, self._charset),
                                               bytes(api_id, self._charset))

    if not self._has_build(api, build):
      raise BravehubNotFoundException()

    return (project, api)

  def _validate_has_asset(self, project_id, api_id, build, asset_id):
    (project, api) = self._validate_has_build(project_id, api_id, build)

    asset = None
    if asset_id:
      asset = api[bytes("builds:{0}-assets-{1}".format(build, asset_id), self._charset)]
      if not asset:
        raise BravehubNotFoundException()

    if asset:
      return (project, api, DynamicObject(json.loads(asset)))

    return (project, api, None)

  def _get_binary_path(self, project_id, api_id, build, role):
    return os.path.join(self.BINARIES_ROOT_FOLDER, project_id, api_id, build, role)

  def _get_configasset_location(self, project_id, api_id, build, asset_id): # pylint: disable=no-self-use
    from src import API_MAJOR_VERSION
    return "/v{0}/projects/{1}/apis/{2}/builds/{3}/configassets/{4}"\
      .format(API_MAJOR_VERSION, project_id, api_id, build, asset_id)
