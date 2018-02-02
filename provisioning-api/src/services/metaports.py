"""Provides the service for managing the provisioning metaports of the system."""

import json
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager
from bravehub_shared.utils.row_locker import OptimisticLocker


class MetaportsService(BravehubService):
  """Provides logic for handling the provisioning metaports and their respective mappings """

  PROVISIONING_METAPORTS_TABLE = "provisioningmetaports"
  #linter doesn't like the length of this variable's name
  PROVISIONING_METAPORTS_MAPPING_TABLE = "provisioningmetaportsmapping" # pylint: disable=invalid-name

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

  @HbaseConnectionManager()
  def save_port_mappings(self, api_id, port_mappings, hbase_manager=None):
    """Stores the association between apis and reserved ports. This actually accelerates
    the provisioning api responsible for retrieving the location of a specific domain and path."""

    connection = hbase_manager.connection
    mapping_tbl = connection.table(self.PROVISIONING_METAPORTS_MAPPING_TABLE)
    mapping_tbl.put(bytes(api_id, self._charset),
                    {
                      b"api:ports": bytes(json.dumps(port_mappings), self._charset)
                    })

  @HbaseConnectionManager()
  def get_port_mappings(self, api_id, hbase_manager=None):
    """Retrieves port mapping for api with api_id. If more than one, retrieves one at random."""
    api_id = bytes(api_id, self._charset)

    connection = hbase_manager.connection
    mapping_tbl = connection.table(self.PROVISIONING_METAPORTS_MAPPING_TABLE)
    metaports_mapping = mapping_tbl.row(api_id, columns=[b"api:ports"])

    if metaports_mapping:
      result = json.loads(metaports_mapping[b"api:ports"].decode(self._charset))
      # in python 3, the values() and keys() methods return views instead of lists
      # https://stackoverflow.com/questions/17431638/get-typeerror-dict-values-object-does-not-support-indexing-when-using-python
      return list(result.values())[0]

    return None
