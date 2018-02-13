"""Provides the contract for working with OAuth2 Bravehub implementation from client applications."""

class OAuth2Client(object):  # pylint: disable=too-few-public-methods
  """Provides the oauth2 helper contract for server side applications."""

  def __init__(self, api_client):
    self._api_client = api_client

  def validate(self, token):
    """Determines if the given token is valid or not. Returns the decrypted token to the
    application."""

    pass
