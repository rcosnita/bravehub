"""
Provides the containers and bindings required for the shared layer to work.
It expects each application to correctly set the config binding with accurate values.
"""
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from bravehub_shared.services.api_client import ApiClient

class CoreContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides the core bindings used in all bravehub modules and micro services."""

  config = Configuration("config")

class ApiClientsContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides all api clients which can be used in bravehub modules and micro services."""

  config_api = Singleton(ApiClient, api_name="configuration-api",
                         cluster_suffix=CoreContainer.config.cluster_suffix)

  logging_api = Singleton(ApiClient, api_name="logging-api",
                          cluster_suffix=CoreContainer.config.cluster_suffix)

  provisioning_api = Singleton(ApiClient, api_name="provisioning-api",
                               cluster_suffix=CoreContainer.config.cluster_suffix)
