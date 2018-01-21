"""
The main entry point for the provisioning api. It bootstraps all routes and related services.
"""

from flask import Flask
from src.ioc import ProvisionerContainer

app = Flask(__name__)  # pylint: disable=invalid-name

@app.route("/")
def hello():  # pylint: disable=missing-docstring
  return "provisioning-api:0.1.0"

ProvisionerContainer.config.update(ProvisionerContainer.provisioner_meta)

from src.views import *  # pylint: disable=wrong-import-position,unused-import
