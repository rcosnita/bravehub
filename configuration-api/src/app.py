"""Provides the main entry point for the configuration api."""

import os

from flask import Flask, send_file
from bravehub_shared.ioc import CoreContainer
from src.ioc import ConfigurationApiContainer

app = Flask(__name__) # pylint: disable=invalid-name

@app.before_first_request
def init_app(): # pylint: disable=missing-docstring
  CoreContainer.config.update({
    "flask_app": app,
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

  ConfigurationApiContainer.config.update(ConfigurationApiContainer.api_meta)

app.send_file = send_file

import src.views # pylint: disable=wrong-import-position,unused-import
