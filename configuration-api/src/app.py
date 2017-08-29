"""Provides the main entry point for the configuration api."""

import os

from flask import Flask
from bravehub_shared.ioc import CoreContainer

app = Flask(__name__) # pylint: disable=invalid-name

@app.before_first_request
def init_app(): # pylint: disable=missing-docstring
  CoreContainer.config.update({
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

import src.views # pylint: disable=wrong-import-position,unused-import
