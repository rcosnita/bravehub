"""Provides all the bindings required by scenegraph service."""
import os
import happybase

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Object, Singleton

from bravehub_shared.ioc import CoreContainer
from bravehub_shared.utils.dynamic_object import DynamicObject

from src.services.scenes import ScenegraphApiService

class ScenegraphApiContainer(DeclarativeContainer): # pylint: disable=too-few-public-methods
  """Provides the container which controls all configuration services lifetime."""
  config = Configuration("scenegraph-api-config")
  api_meta = DynamicObject({
    "name": "scenegraph-api",
    "version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    },
    "thrift_server": os.environ["HBASE_THRIFT_API"]
  })

  hbase_conn_pool = Object(happybase.ConnectionPool(size=300, host=api_meta.thrift_server,
                                                    autoconnect=True, timeout=2000,
                                                    table_prefix='bravehub',
                                                    table_prefix_separator=":"))

  scenes_service = Singleton(ScenegraphApiService, flask_app=CoreContainer.config.flask_app,
                             conn_pool=hbase_conn_pool,
                             charset=CoreContainer.DEFAULT_CHARSET)
