"""
Provides the containers and bindings required for the shared layer to work.
It expects each application to correctly set the config binding with accurate values.
"""
import os
from urllib import request

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from bravehub_shared.services.id_generator import IdGeneratorService
from bravehub_shared.services.api_client import ApiClient
from bravehub_shared.services.file_system import LocalFileSystem

class CoreContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides the core bindings used in all bravehub modules and micro services."""

  config = Configuration("config")

  DEFAULT_CHARSET = "utf-8"

  file_system = Singleton(LocalFileSystem, mount_location=os.environ.get("NAS_MOUNT"))
  id_service = Singleton(IdGeneratorService, charset=DEFAULT_CHARSET)

class ApiClientsContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides all api clients which can be used in bravehub modules and micro services."""

  config_api = Singleton(ApiClient, api_name="configuration-api",
                         cluster_suffix=CoreContainer.config.cluster_suffix,
                         http_client=request, api_port=5000)

  logging_api = Singleton(ApiClient, api_name="logging-api",
                          cluster_suffix=CoreContainer.config.cluster_suffix,
                          http_client=request, api_port=5010)

  provisioning_api = Singleton(ApiClient, api_name="provisioning-api",
                               cluster_suffix=CoreContainer.config.cluster_suffix,
                               http_client=request, api_port=5020)
