"""This module provides all the endpoints and resources supported by the configuration api."""

from src import API_FULL_VERSION
from src.app import app # pylint: disable=cyclic-import

@app.route("/")
def version(): # pylint: disable=missing-docstring
  return "Version: {0}".format(API_FULL_VERSION)

import src.apis # pylint: disable=wrong-import-position,unused-import
import src.owners # pylint: disable=wrong-import-position,unused-import
import src.projects # pylint: disable=wrong-import-position,unused-import
