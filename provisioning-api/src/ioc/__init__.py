"""Provides all the bindings for the provisioning api and provisioner service."""

import os
import happybase

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Object, Singleton

from bravehub_shared.ioc import ApiClientsContainer, CoreContainer
from bravehub_shared.utils.dynamic_object import DynamicObject

import docker

from src.provisioner.image_builder import DockerImageBuilder
from src.provisioner.image_runner import DockerEngineImageRunner
from src.provisioner.provisioner import Provisioner

class ProvisionerContainer(DeclarativeContainer):  # pylint: disable=too-few-public-methods
  """Provides all the bindings required by the provisioner service."""

  provisioner_meta = DynamicObject({
    "version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    },
    "thrift_server": os.environ["HBASE_THRIFT_API"]
  })

  hbase_conn_pool = Object(happybase.ConnectionPool(size=10, host=provisioner_meta.thrift_server,
                                                    autoconnect=False, timeout=2000,
                                                    table_prefix='bravehub',
                                                    table_prefix_separator=":"))

  docker_client = Object(docker.from_env())

  docker_image_builder = Singleton(DockerImageBuilder, file_system=CoreContainer.file_system,
                                   docker_client=docker_client,
                                   default_charset=CoreContainer.DEFAULT_CHARSET)

  docker_image_runner = Singleton(DockerEngineImageRunner, hbase_conn_pool=hbase_conn_pool,
                                  default_charset=CoreContainer.DEFAULT_CHARSET,
                                  docker_client=docker_client)

  provisioner = Singleton(Provisioner,
                          sleeping_period=10, hbase_conn_pool=hbase_conn_pool,
                          default_charset=CoreContainer.DEFAULT_CHARSET,
                          config_api=ApiClientsContainer.config_api,
                          config_api_version="v0.1", image_builder=docker_image_builder,
                          image_runner=docker_image_runner)
