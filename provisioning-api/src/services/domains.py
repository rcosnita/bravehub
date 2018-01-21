"""Provides the service for managing the domains associated to APIs."""

from bravehub_shared.exceptions.bravehub_exceptions import BravehubNotFoundException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager


class DomainService(BravehubService):
  """Provides logic to handle the domains in the database"""
  DOMAINS_TABLE = "domains"

  @HbaseConnectionManager()
  def get_api_id_for_domain_and_path(self, domain, path, hbase_manager=None):
    """Fetch the id of the API associated with the given domain and path"""

    domain = bytes(domain, self._charset)

    connection = hbase_manager.connection
    domains_table = connection.table(self.DOMAINS_TABLE)
    domains = domains_table.scan(row_prefix=domain)

    if not domains:
      raise BravehubNotFoundException()

    for key, data in domains:
      # remove the domain part from the key, to get the subdomain
      # i.e. myDomain.com/news/v1/article_id/ returns /news/v1/article_id
      decoded_key = key.decode(self._charset)
      sub_domain = decoded_key[len(domain):len(decoded_key)]

      if path.startswith(sub_domain):
        api_id = data[b"api:id"].decode(self._charset)
        return api_id

    raise BravehubNotFoundException()

  @HbaseConnectionManager()
  def create_domain(self, domain, path, api_id, hbase_manager=None):
    """Add a new entry in the domains table linking a domain and path to an api"""
    path = domain + path

    connection = hbase_manager.connection
    domains_table = connection.table(self.DOMAINS_TABLE)
    domains_table.put(bytes(path, self._charset),
                      {
                        b"api:id": bytes(api_id, self._charset)
                      })
