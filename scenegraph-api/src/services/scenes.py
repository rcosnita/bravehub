"""Provides the service which provides management operations for scene graphs."""
import json

from bravehub_shared.exceptions.bravehub_exceptions import BravehubNotFoundException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager
from bravehub_shared.utils.dynamic_object import DynamicObject

class ScenegraphApiService(BravehubService):
  """Provides the scenegraph CRUD operations."""

  SCENES_TABLE = "scenegraphs"

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def get_scene(self, scene_id_str, hbase_manager=None):
    """Retrieve the specified scene from the persistent storage."""

    conn = hbase_manager.connection
    scenes_tbl = conn.table(self.SCENES_TABLE)
    scene_id = bytes(scene_id_str, self._charset)
    scene_row = scenes_tbl.row(scene_id)

    if not scene_row:
      raise BravehubNotFoundException()

    scene = json.loads(scene_row[b"scene:descriptor"].decode(self._charset))
    return scene

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def update_scene(self, scene_id_str, scene_body, hbase_manager=None):
    """Updates an existing scenegraph with the given scene body."""

    conn = hbase_manager.connection
    scene_body = DynamicObject(scene_body)
    scene_body.id = scene_id_str

    self._create_update_scene(scene_body, conn)

    return None, 204, {}

  def _create_update_scene(self, scene_body, conn):
    scene_id = bytes(scene_body.id, self._charset)
    scenes_tbl = conn.table(self.SCENES_TABLE)

    scenes_tbl.put(scene_id, {
      b"scene:descriptor": json.dumps(scene_body)
    })

  def _get_scene_location(self, scene_id):  # pylint: disable=no-self-use
    from src import API_VERSION
    return "/v{0}/scenes/{1}".format(API_VERSION, scene_id)
