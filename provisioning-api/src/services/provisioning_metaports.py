"""Provides the service for managing the provisioning metaports of the system."""

from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager
from bravehub_shared.utils.row_locker import OptimisticLocker


class ProvisioningMetaportsService(BravehubService):
  """Provides logic for handling the provisioning metaports mappings """
  PROVISIONING_METAPORTS_TABLE = "provisioningmetaports"

  @HbaseConnectionManager()
  def reserve_next_free_port(self, api_id, hbase_manager=None):
    """It relies on the hbase provisioningmetaports table in order to obtain an available port. It
    uses an optimistic locking strategy in order to solve the potential concurrency issues."""

    conn = hbase_manager.connection
    ports_tbl = conn.table(self.PROVISIONING_METAPORTS_TABLE)

    port_record = ports_tbl.scan(filter="SingleColumnValueFilter('attrs','status',=,'binary:free')",
                                 limit=1)

    try:
      port_record = next(port_record)
    except StopIteration:
      # TODO(cosnita) implement proper signaling for missing ports
      raise ValueError("No free ports ... Go away ...")

    port_id = port_record[0]
    port_id_str = port_id.decode(self._charset)

    # We know that the format is guid-port -> used for making sure we don't end up with a hot
    # region.
    port = port_id_str[port_id_str.rfind("-") + 1:]
    expected_status = bytes(api_id, self._charset)

    with OptimisticLocker(self.conn_pool, self._charset, self.PROVISIONING_METAPORTS_TABLE,
                          port_id,
                          when_acquired=lambda conn, tbl: \
                            tbl.put(port_id, {b"attrs:status": expected_status})) as lock:
      if not lock.locked:
        return

      return int(port)
