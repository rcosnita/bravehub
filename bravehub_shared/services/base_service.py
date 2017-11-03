"""Provides the foundation for implementing Bravehub services integrated with flask handlers."""

import os

PLATFORM_DEBUG = (os.environ.get("BRAVEHUB_DEBUG") or "0") == "1"

class BravehubService(object): # pylint: disable=too-few-public-methods
  """Provides the topmost class which must be subclassed in order to implement Bravehub
  services. It provides some useful properties which makes the service integrates nicely
  with some other platform defaults."""

  def __init__(self, flask_app, conn_pool, charset):
    self._flask_app = flask_app
    self._conn_pool = conn_pool
    self._charset = charset

  @property
  def flask_app(self): # pylint: disable=missing-docstring
    return self._flask_app

  @property
  def conn_pool(self): # pylint: disable=missing-docstring
    return self._conn_pool
