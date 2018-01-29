"""Provides the service for managing the provisioning metaports mappings from the system."""

import json
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager

class ProvisioningMetaportsMappingService(BravehubService):
  """Provides logic for handling the provisioning metaports mappings """
  #linter doesn't like the length of this variable's name
  PROVISIONING_META_PORTS_MAPPING_TABLE = "provisioningmetaportsmapping" # pylint: disable=invalid-name

  @HbaseConnectionManager()
  def save_port_mappings(self, api_id, port_mappings, hbase_manager=None):
    """Stores the association between apis and reserved ports. This actually accelerates
    the provisioning api responsible for retrieving the location of a specific domain and path."""

    connection = hbase_manager.connection
    mapping_tbl = connection.table(self.PROVISIONING_META_PORTS_MAPPING_TABLE)
    mapping_tbl.put(bytes(api_id, self._charset),
                    {
                      b"api:ports": bytes(json.dumps(port_mappings), self._charset)
                    })

  @HbaseConnectionManager()
  def get_port_mappings(self, api_id, hbase_manager=None):
    """Retrieves port mapping for api with api_id. If more than one, retrieves one at random."""
    api_id = bytes(api_id, self._charset)

    connection = hbase_manager.connection
    mapping_tbl = connection.table(self.PROVISIONING_META_PORTS_MAPPING_TABLE)
    metaports_mapping = mapping_tbl.row(api_id, columns=[b"api:ports"])

    if metaports_mapping:
      result = json.loads(metaports_mapping[b"api:ports"].decode(self._charset))
      # in python 3, the values() and keys() methods return views instead of lists
      # https://stackoverflow.com/questions/17431638/get-typeerror-dict-values-object-does-not-support-indexing-when-using-python
      return list(result.values())[0]

    return None
