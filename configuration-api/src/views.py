"""This module provides all the endpoints and resources supported by the configuration api."""

from bravehub_shared.ioc import ApiClientsContainer
from src.app import app

@app.route("/")
def hello(): # pylint: disable=missing-docstring
  api_client = ApiClientsContainer.config_api()
  return str(api_client)
