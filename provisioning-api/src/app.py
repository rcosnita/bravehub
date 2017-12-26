import json
import os
from flask import Flask

from flask import request

app = Flask(__name__)

CURR_FOLDER = os.path.dirname(os.path.realpath(__file__))
PLATFORM_SUFFIX = os.environ["BRAVEHUB_SUFFIX"]
PLATFORM_APIS_FILE = "platform-apis.json"

core_apis_config = {}

@app.before_first_request
def init_app():
  global core_apis_config

  with open(os.path.join(CURR_FOLDER, PLATFORM_APIS_FILE)) as core_apis_file:
    core_apis_config = json.load(core_apis_file)
    core_apis_config = {
       "{0}.{1}".format(public_domain, PLATFORM_SUFFIX): \
        {
          "workerDomain": "{0}.{1}".format(cfg["prefix"], PLATFORM_SUFFIX),
          "workerPort": cfg["port"]
        }
       for public_domain, cfg in core_apis_config.items()
    }

@app.route("/")
def hello():
  return "provisioning-api:0.1.0"

def _serve_platform_api(domain):
  """In case the given domain is a platform service domain, route the request to the platform
  infrastructure."""

  platform_api = core_apis_config.get(domain)
  if not platform_api:
    return

  return app.response_class(response=json.dumps(platform_api),
                            status=200,
                            mimetype="application/json")

@app.route("/v1/domains")
def resolve_domains():
  domain = request.args.get("domain", "")
  path = request.args.get("path", "")  # TODO(cosnita) must be used by @aturlac.

  platform_api = _serve_platform_api(domain)
  if platform_api:
    return platform_api

  err_msg = "Domain {0} not deployed on {1}.".format(domain, PLATFORM_SUFFIX)
  return app.response_class(response=json.dumps({"message": err_msg}),
                            status=404,
                            mimetype="application/json")
