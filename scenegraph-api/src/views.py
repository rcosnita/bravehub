"""Provides all the routes required to implement the scenegraph REST service."""

import json

from flask import request

from src import API_VERSION
from src.app import app # pylint: disable=cyclic-import
from src.ioc import ScenegraphApiContainer

def _get_scenegraph_service():
  return ScenegraphApiContainer.scenes_service()

@app.route("/")
def version():  # pylint: disable=missing-docstring
  return json.dumps(ScenegraphApiContainer.api_meta)

@app.route("/v{0}/scenes/<scene_id>".format(API_VERSION), methods=["GET", "PUT"])
def manage_scene(scene_id):
  """Retrieve the requested scenegraph."""
  scenes_service = _get_scenegraph_service()

  if request.method == "GET":
    return scenes_service.get_scene(scene_id)
  elif request.method == "PUT":
    scene_body = request.get_json(force=True)
    return scenes_service.update_scene(scene_id, scene_body)

  raise ValueError("Operation not supported ...")
