"""Provides the service for managing the owners from the system."""

from bravehub_shared import CURRENT_USER
from bravehub_shared.exceptions.bravehub_exceptions import BravehubNotImplementedException
from bravehub_shared.services.base_service import BravehubService
from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator
from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager

class OwnerService(BravehubService):
  """Provides the implementation for managing owners from the system. The persistence
  logic is tightly coupled in the service."""

  @FlaskResponseGenerator()
  @HbaseConnectionManager()
  def get_owner(self, owner_id, hbase_manager):
    """Fetch an existing owner from the database."""

    owner_data = None
    owner_id = bytes(CURRENT_USER, self._charset)

    connection = hbase_manager.connection
    owners_tbl = connection.table("projectowners")
    owner = owners_tbl.row(owner_id, columns=[b"attrs:email", b"attrs:authentication_provider",
                                              b"attrs:authorization_provider"])

    owner_data = {
      "email": owner[b"attrs:email"].decode(self._charset),
      "authenticationProvider": owner[b"attrs:authentication_provider"].decode(self._charset),
      "authorizationProvider": owner[b"attrs:authorization_provider"].decode(self._charset)
    }

    return owner_data

  @FlaskResponseGenerator()
  def create_owner(self, owner_data): # pylint: disable=unused-argument,no-self-use
    """Create a new owner starting from the given data."""

    raise BravehubNotImplementedException()
