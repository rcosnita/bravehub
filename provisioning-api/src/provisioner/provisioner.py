#!/usr/bin/env python3

"""Provides an implementation which transform states from database into actual
infrastructure deployment. In this initial implementation we made some simplifying
assumptions:

* Each provisioner will scan the hbase bravehub:provisioningtasks table.
* The first available project will be locked by provisioner until all states are deployed.

Like this, we can simulate a queueing system and we can scale horizontally without actually using
a dedicate queueing infrastructure."""

import json
import os
import time
import uuid

from urllib.error import HTTPError

import ptvsd


from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager
from bravehub_shared.utils.row_locker import OptimisticLocker
from src.provisioner.image_builder import ImageBuilderContext
from src.provisioner.image_runner import ImageRunnerContext

class Provisioner(object):  # pylint: disable=too-many-instance-attributes
  """Provisioner provides the mechanism for polling new states which must be deployed in the
  infrastructure. Based on the environment where it is running it might use various
  image builders / runners."""

  def __init__(self, sleeping_period, hbase_conn_pool,  # pylint: disable=too-many-arguments
               default_charset, config_api, config_api_version, image_builder, image_runner):
    self._provisioner_id = uuid.uuid4()
    self._sleeping_period = sleeping_period
    self._hbase_conn_pool = hbase_conn_pool
    self._default_charset = default_charset
    self._config_api = config_api
    self._config_api_version = config_api_version
    self._image_builder = image_builder
    self._image_runner = image_runner

  @property
  def conn_pool(self): # pylint: disable=missing-docstring
    return self._hbase_conn_pool

  def run(self):
    """Tries to identify the next project state we want to apply to the infrastructure."""
    while True:
      self._run_next_task()
      time.sleep(self._sleeping_period)

  @HbaseConnectionManager(raise_error=False)
  def _run_next_task(self, hbase_manager=None):
    if not hbase_manager:
      return

    project = None
    project_id = None
    project_data = None

    conn = hbase_manager.connection
    tasks_tbl = conn.table("provisioningtasks")
    project = tasks_tbl.scan(filter="SingleColumnValueFilter('attrs','status',=,'binary:NEW')",
                             limit=1)

    try:
      project = next(project)
    except StopIteration:
      return

    project_id = project[0]
    project_data = project[1]

    with OptimisticLocker(self._hbase_conn_pool, self._default_charset, "provisioningtasks",
                          project_id,
                          when_acquired=lambda conn, tbl: \
                            tbl.put(project_id, {b"attrs:status": "PROCESSING"}),
                          when_released=lambda conn, tbl: \
                            self._remove_task(project_id)) as lock:
      if not lock.locked:
        return

      # TODO(cosnita) Add proper logging.
      print("Task {0} locked.".format(project_id))

      for state_key, state_id in [
          (state_id, state_id.replace(b"states:", b"").decode(self._default_charset))
          for state_id in project_data
          if state_id.startswith(b"states:")]:
        if self._process_state(project_id.decode(self._default_charset),
                               state_id,
                               json.loads(project_data[state_key].decode(self._default_charset))):
          self._remove_state(project_id, state_key)

  @HbaseConnectionManager()
  def _remove_state(self, project_id, state_key, hbase_manager=None):
    """Removes a processed state from the provisioning tasks."""

    conn = hbase_manager.connection
    tasks_tbl = conn.table("provisioningtasks")
    tasks_tbl.delete(project_id, [state_key])

    # TODO(cosnita) Add proper logging.
    print("Removed state {0}".format(state_key.decode(self._default_charset)))

  @HbaseConnectionManager()
  def _remove_task(self, project_id, hbase_manager=None):  # pylint: disable=no-self-use
    """Once a locked task is completely processed we completely remove the record."""

    conn = hbase_manager.connection
    tasks_tbl = conn.table("provisioningtasks")
    tasks_tbl.delete(project_id, [b"attrs:lock", b"attrs:status"])

    # TODO(cosnita) Add proper logging.
    print("Task {0} removed.".format(project_id))

  def _process_state(self, project_id, state_id, state_body):
    """We cast the current state to relevant information which can be used to deploy the service."""
    state = DynamicObject(state_body)
    api_id = state.api_id

    api_path = "/{0}/projects/{1}/apis/{2}".format(self._config_api_version, project_id, api_id)

    api_data = None

    try:
      api_data = self._config_api.get_json(api_path)

      if api_data.status_code != 200:
        # TODO(cosnita) add proper error handling or retry mechanism.
        raise ValueError("Fuck off")
    except HTTPError as ex:
      # TODO(cosnita) add proper error handling or retry mechanism.
      print("Fatal error .... Skipping state {0} for now ...".format(state_id))
      return False

    image_ctx = ImageBuilderContext(project_id=project_id, api_id=api_id, build_num=state.build_num,
                                    config_data=api_data.body)

    try:
      image_tag = self._image_builder.build_image(image_ctx)
      runner_ctx = ImageRunnerContext(image_tag, api_data.body.exposedPorts)
      self._image_runner.run_image(image_ctx, runner_ctx)
    except Exception as ex:  # pylint: disable=broad-except
      # TODO(cosnita) add proper handling
      print(ex)
      print("Fatal error .... Skipping state {0} for now ...".format(state_id))
      return False

    return True

if __name__ == "__main__":
  from src.ioc import CoreContainer, ProvisionerContainer

  if os.environ.get("BRAVEHUB_DEBUG") == "1":
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3020))

  CoreContainer.config.update({
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

  PROVISIONER = ProvisionerContainer.provisioner()
  PROVISIONER.run()
