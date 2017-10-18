"""Provides the algorithm for an optimistic lock strategy implemented on top of HBase."""

from contextlib import AbstractContextManager
import uuid

class OptimisticLocker(AbstractContextManager): # pylint: disable=too-few-public-methods,too-many-instance-attributes
  """Provides the optimistic locker built on top of hbase. Internally, it does a read after write
  in order to determine if the row is truly locked or not."""

  def __init__(self, hbase_conn_pool, default_charset, tbl_name, row_id, expected_lock=None, # pylint: disable=too-many-arguments
               when_acquired=None, when_released=None):
    super(OptimisticLocker).__init__()
    self._hbase_conn_pool = hbase_conn_pool
    self._default_charset = default_charset
    self._tbl_name = tbl_name
    self._row_id = row_id
    self._is_locked = False
    self._expected_lock = expected_lock or bytes(str(uuid.uuid4()), self._default_charset)
    self._when_acquired = when_acquired or (lambda conn, tbl: False)
    self._when_released = when_released or (lambda conn, tbl: False)

  @property
  def locked(self): #pylint: disable=missing-docstring
    return self._is_locked

  def __enter__(self):
    locked = None

    with self._hbase_conn_pool.connection() as conn:
      tbl = conn.table(self._tbl_name)
      record = tbl.row(self._row_id)

      if not record:
        self._is_locked = False
        return self

      attrs_lock = record.get(b"attrs:lock")

      if not attrs_lock:
        tbl.put(self._row_id, {b"attrs:lock": self._expected_lock})
        record = tbl.row(self._row_id)

        locked = (record and record[b"attrs:lock"] == self._expected_lock)

      if locked:
        self._when_acquired(conn, tbl)
        self._is_locked = True

    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    # TODO(cosnita) add proper error handling in here.
    if exc_value:
      print(exc_value)
      print(exc_tb)
      return

    with self._hbase_conn_pool.connection() as conn:
      tbl = conn.table(self._tbl_name)
      self._when_released(conn, tbl)
