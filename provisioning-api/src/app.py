"""
The main entry point for the provisioning api. It bootstraps all routes and related services.
"""

import json
import os
import ptvsd

from flask import Flask
from flask import request

app = Flask(__name__)  # pylint: disable=invalid-name

CURR_FOLDER = os.path.dirname(os.path.realpath(__file__))
PLATFORM_SUFFIX = os.environ["BRAVEHUB_SUFFIX"]
PLATFORM_APIS_FILE = "platform-apis.json"

CORE_APIS_CONFIG = {}

@app.before_first_request
def init_app():  # pylint: disable=missing-docstring
  global CORE_APIS_CONFIG  # pylint: disable=global-statement

  if os.environ.get("BRAVEHUB_DEBUG") == "1":
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3020))

  with open(os.path.join(CURR_FOLDER, PLATFORM_APIS_FILE)) as core_apis_file:
    CORE_APIS_CONFIG = json.load(core_apis_file)
    CORE_APIS_CONFIG = {
      "{0}.{1}".format(public_domain, PLATFORM_SUFFIX): \
        {
          "workerDomain": "{0}.{1}".format(cfg["prefix"], PLATFORM_SUFFIX),
          "workerPort": cfg["port"]
        }
      for public_domain, cfg in CORE_APIS_CONFIG.items()
    }

@app.route("/")
def hello():  # pylint: disable=missing-docstring
  return "provisioning-api:0.1.0"

def _serve_platform_api(domain):
  """In case the given domain is a platform service domain, route the request to the platform
  infrastructure."""

  platform_api = CORE_APIS_CONFIG.get(domain)
  if not platform_api:
    return

  return app.response_class(response=json.dumps(platform_api),
                            status=200,
                            mimetype="application/json")

@app.route("/v0.1/domains")
def resolve_domains():
  """Returns information about the given domain and path. It first searches the list of
  platform apis and then user defined domains and apis.

  In bravehub, it is possible to have a path belonging to a domain hosted on a completely
  separated infrastructure than other paths belonging to the same domain. This is how
  micro services are expected to work.
  """

  domain = request.args.get("domain", "")
  path = request.args.get("path", "")  # pylint: disable=unused-variable
  # TODO(cosnita) must be used by @aturlac.

  platform_api = _serve_platform_api(domain)
  if platform_api:
    return platform_api

  err_msg = "Domain {0} not deployed on {1}.".format(domain, PLATFORM_SUFFIX)
  return app.response_class(response=json.dumps({"message": err_msg}),
                            status=404,
                            mimetype="application/json")
