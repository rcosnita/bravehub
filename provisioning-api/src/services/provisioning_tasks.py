"""Provides the service for managing the provisioning tasks from the system."""
import json

from bravehub_shared.exceptions.bravehub_exceptions import BravehubNotFoundException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager

class ProvisioningTaskService(BravehubService):
  """Provides the logic for managing provisioning tasks."""

  PROVISIONING_TASK_TABLE = "provisioningtasks"

  def __init__(self, flask_app, conn_pool, charset, id_service): # pylint: disable=too-many-arguments
    super(ProvisioningTaskService, self).__init__(flask_app, conn_pool, charset)
    self._id_service = id_service

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def get_task(self, project_id, hbase_manager=None):
    """Fetch an existing task from the database."""

    project_id = bytes(project_id, self._charset)

    connection = hbase_manager.connection
    provisioning_tasks_table = connection.table(self.PROVISIONING_TASK_TABLE)
    provisioning_tasks = provisioning_tasks_table.row(project_id)

    if not provisioning_tasks:
      raise BravehubNotFoundException()

    tasks = []
    for key in provisioning_tasks.keys():
      states_data = json.loads(provisioning_tasks[key].decode(self._charset))
      tasks.append({key.decode(self._charset): states_data})

    return {"items": tasks}

  @HbaseConnectionManager()
  def save_task(self, task, hbase_manager=None):
    """Save a new task to the database"""
    task["states"] = self._id_service.generate()
    connection = hbase_manager.connection
    provisioning_tasks_table = connection.table(self.PROVISIONING_TASK_TABLE)
    provisioning_tasks_table.put(bytes(task["projectId"], self._charset),
                                 {
                                   bytes("states:{0}".format(task["states"]), self._charset): json.dumps({  # pylint: disable=line-too-long
                                     "api_id": task["apiId"],
                                     "build_num": task["build"]
                                   })
                                 })

    return task
