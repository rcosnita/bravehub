"""Provides the api code for managing owners from the system."""
from flask import request

from src import API_MAJOR_VERSION, ConfigurationApiContainer
from src.app import app

def _get_owner_service():
  return ConfigurationApiContainer.owner_service()

@app.route("/v{0}/owners".format(API_MAJOR_VERSION), methods=["POST"])
def manage_owners():
  """Provides the logic for creating a new owner."""

  owner_data = request.get_json(force=True)
  return _get_owner_service().create_owner(owner_data)

@app.route("/v{0}/owners/<owner_id>".format(API_MAJOR_VERSION), methods=["GET", "PUT"])
def manage_owner(owner_id):
  """Provides the logic for managing a specific owner."""

  return _get_owner_service().get_owner(owner_id)
