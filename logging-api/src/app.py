"""
The main entrypoint for launching the logging api.
"""

import json
import os
import ptvsd

from flask import Flask

app = Flask(__name__)  # pylint: disable=invalid-name

@app.before_first_request
def init_app():  # pylint: disable=missing-docstring
  if os.environ.get("BRAVEHUB_DEBUG") == "1":
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3010))

@app.route("/")
def hello():  # pylint: disable=missing-docstring
  return json.dumps({
    "api_name": "logging-api:0.0.1",
    "api_version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    }
  })
