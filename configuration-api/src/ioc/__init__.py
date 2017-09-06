"""
Provides all the bindings for the configuration api service.
"""
import os
import happybase

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Object, Singleton

from bravehub_shared.ioc import CoreContainer
from bravehub_shared.utils.dynamic_object import DynamicObject
from src.services.apis import ProjectApiService
from src.services.owners import OwnerService
from src.services.projects import ProjectService

class ConfigurationApiContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides the container which controls all configuration services lifetime."""
  config = Configuration("config-api-config")
  api_meta = DynamicObject({
    "version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    },
    "thrift_server": os.environ["HBASE_THRIFT_API"]
  })

  hbase_conn_pool = Object(happybase.ConnectionPool(size=10, host=api_meta.thrift_server,
                                                    table_prefix='bravehub',
                                                    table_prefix_separator=":"))

  owner_service = Singleton(OwnerService, flask_app=CoreContainer.config.flask_app,
                            conn_pool=hbase_conn_pool,
                            charset=CoreContainer.DEFAULT_CHARSET)

  project_service = Singleton(ProjectService, flask_app=CoreContainer.config.flask_app,
                              conn_pool=hbase_conn_pool,
                              charset=CoreContainer.DEFAULT_CHARSET)

  api_service = Singleton(ProjectApiService, flask_app=CoreContainer.config.flask_app,
                          conn_pool=hbase_conn_pool,
                          charset=CoreContainer.DEFAULT_CHARSET,
                          project_service=project_service)
