"""Provides a happy base wrapper which is capable to detect broken connections
before actually executing arbitrary code."""
import time

class HbaseConnectionManager(object): # pylint: disable=too-few-public-methods
  """Sends a ping before actually executing the inner code. In case an exception
  appears it retries for several times (equals the size of the connection pool).

  In order for this decorator to work each self argument must provide a conn_pool
  property."""

  class HbaseConnection(object): # pylint: disable=too-few-public-methods
    """Provides an extensible model for injecting hbase valid connections into decorated methods."""

    def __init__(self, connection):
      self._connection = connection

    @property
    def connection(self): # pylint: disable=missing-docstring
      return self._connection

  def __init__(self, conn_pool_property="conn_pool"):
    self._conn_pool_property = conn_pool_property
    self._hbase_connection_arg = "hbase_manager"
    self._healthcheck_table = "healthchecks"
    self._rowid = b"1"
    self._last_check = 0
    self._check_threshold = 20 # number of seconds for which we skip the health checks

  def _is_healthy(self, conn):
    """This is an extremely simple check which determines if the current connection is healthy
    or not."""

    try:
      tbl = conn.table(self._healthcheck_table)
      if not tbl.row(self._rowid):
        return False

      return True
    except: # pylint: disable=bare-except
      return False

  def __call__(self, method):
    def handle_method(*args, **kwargs): # pylint: disable=missing-docstring
      fn_self = args[0]
      conn_pool = getattr(fn_self, self._conn_pool_property)

      num_retries = 0
      max_retries = 1
      check_health = False

      if time.time() - self._last_check > self._check_threshold:
        check_health = True
        max_retries = conn_pool._queue.qsize() # pylint: disable=protected-access
        self._last_check = time.time()

      while num_retries < max_retries:
        with conn_pool.connection() as conn:
          if check_health and not self._is_healthy(conn):
            num_retries += 1
            conn._refresh_thrift_client() # pylint: disable=protected-access
            continue

          kwargs[self._hbase_connection_arg] = HbaseConnectionManager.HbaseConnection(conn)
          return method(*args, **kwargs)

      raise ValueError("No more hbase connections: %s attempts." % num_retries)

    handle_method.__doc__ = method.__doc__

    return handle_method
