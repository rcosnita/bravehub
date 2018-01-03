"""Provides the main entry point for the configuration api."""

import os
import ptvsd

from flask import Flask, send_file
from flask_cors import CORS

from bravehub_shared.ioc import CoreContainer
from src.ioc import ConfigurationApiContainer

app = Flask(__name__) # pylint: disable=invalid-name
CORS(app, expose_headers="Location")

@app.before_first_request
def init_app(): # pylint: disable=missing-docstring
  if os.environ.get("BRAVEHUB_DEBUG") == "1":
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3000))

  CoreContainer.config.update({
    "flask_app": app,
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

  ConfigurationApiContainer.config.update(ConfigurationApiContainer.api_meta)

app.send_file = send_file

import src.views # pylint: disable=wrong-import-position,unused-import
