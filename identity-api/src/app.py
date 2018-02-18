"""
The main entrypoint for launching the identity api.
"""

import json
import os

from flask import Flask
import ptvsd

app = Flask(__name__)  # pylint: disable=invalid-name

@app.before_first_request
def init_app():  # pylint: disable=missing-docstring
  if os.environ.get("BRAVEHUB_DEBUG") == "1":
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3050))

@app.route("/")
def version():  # pylint: disable=missing-docstring
  return json.dumps({
    "api_name": "identity-api:0.1.0",
    "api_version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    }
  })
