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

from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.utils.row_locker import OptimisticLocker
from src.provisioner.image_builder import ImageBuilderContext
from src.provisioner.image_runner import ImageRunnerContext

class Provisioner(object):
  def __init__(self, sleeping_period, hbase_conn_pool,
               default_charset, config_api, config_api_version, image_builder, image_runner):
    self._provisioner_id = uuid.uuid4()
    self._sleeping_period = sleeping_period
    self._hbase_conn_pool = hbase_conn_pool
    self._default_charset = default_charset
    self._config_api = config_api
    self._config_api_version = config_api_version
    self._image_builder = image_builder
    self._image_runner = image_runner

  def run(self):
    """Tries to identify the next project state we want to apply to the infrastructure."""
    while True:
      self._run_next_task()
      time.sleep(self._sleeping_period)

  def _run_next_task(self):
    project = None
    project_id = None
    project_data = None

    with self._hbase_conn_pool.connection() as conn:
      tasks_tbl = conn.table("provisioningtasks")
      project = tasks_tbl.scan(filter="SingleColumnValueFilter('attrs','status',=,'binary:NEW')",
                               limit=1)

      try:
        project = next(project)
      except StopIteration:
        return

      project_id = project[0]
      project_data = project[1]

    with OptimisticLocker(self._hbase_conn_pool, self._default_charset, "provisioningtasks", project_id,
                          when_acquired=lambda conn, tbl: tbl.put(project_id, { b"attrs:status": "PROCESSING" }),
                          when_released=lambda conn, tbl: self._remove_task(project_id)) as lock:
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

  def _remove_state(self, project_id, state_key):
    """Removes a processed state from the provisioning tasks."""
    with self._hbase_conn_pool.connection() as conn:
      tasks_tbl = conn.table("provisioningtasks")
      tasks_tbl.delete(project_id, [ state_key ])

      # TODO(cosnita) Add proper logging.
      print("Removed state {0}".format(state_key.decode(self._default_charset)))

  def _remove_task(self, project_id):
    """Once a locked task is completely processed we completely remove the record."""
    with self._hbase_conn_pool.connection() as conn:
      tasks_tbl = conn.table("provisioningtasks")
      tasks_tbl.delete(project_id, [ b"attrs:lock", b"attrs:status" ])

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
      runner_ctx = ImageRunnerContext(image_tag, api_data.exposedPorts)
      self._image_runner.run_image(image_ctx, runner_ctx)
    except Exception as ex:
      # TODO(cosnita) add proper handling
      print(ex)
      print("Fatal error .... Skipping state {0} for now ...".format(state_id))
      return False

    return True

if __name__ == "__main__":
  from src.ioc import CoreContainer, ProvisionerContainer
  CoreContainer.config.update({
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

  provisioner = ProvisionerContainer.provisioner()
  provisioner.run()
