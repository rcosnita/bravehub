"""Provides the api code for managing project apis from the system."""
import json
import os
import ptvsd

from flask import request

from bravehub_shared.utils.flask_response_generator import FlaskResponseGenerator
from bravehub_shared.ioc import CoreContainer
from src import API_MAJOR_VERSION
from src.app import app
from src.ioc import ProvisionerContainer

CURR_FOLDER = os.path.dirname(os.path.realpath(__file__))
PLATFORM_SUFFIX = os.environ["BRAVEHUB_SUFFIX"]
PLATFORM_APIS_FILE = "platform-apis.json"
WORKER_DOMAIN = os.environ["WORKER_DOMAIN"]

CORE_APIS_CONFIG = {}

CONFIGASSET_CONTENT_TYPE = "application/vnd.bravehub.configurationasset-binary"
DROPLET_CONTENT_TYPE = "application/vnd.bravehub.droplet-binary"

@app.before_first_request
def init_app():  # pylint: disable=missing-docstring
  global CORE_APIS_CONFIG  # pylint: disable=global-statement

  CoreContainer.config.update({
    "flask_app": app,
    "cluster_suffix": os.environ["BRAVEHUB_SUFFIX"]
  })

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

def _get_provisioning_tasks_service():
  return ProvisionerContainer.provisioning_tasks_service()

def _get_domains_service():
  return ProvisionerContainer.domain_service()

def _get_metaports_service():
  return ProvisionerContainer.metaports_service()

def _serve_platform_api(domain):
  """In case the given domain is a platform service domain, route the request to the platform
  infrastructure."""

  platform_api = CORE_APIS_CONFIG.get(domain)
  if not platform_api:
    return

  return app.response_class(response=json.dumps(platform_api),
                            status=200,
                            mimetype="application/json")

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/states".format(API_MAJOR_VERSION), methods=["GET"])  # pylint: disable=line-too-long
def get_project_build_states(project_id, api_id, build):  # pylint: disable=unused-argument
  """Get the build states for the given project and API"""
  pass

@app.route("/v{0}/projects/<project_id>/apis/<api_id>/builds/<build>/states".format(API_MAJOR_VERSION), methods=["POST"])  # pylint: disable=line-too-long
def create_project_build_state(project_id, api_id, build):
  """Create a new state"""
  data = request.data
  data_dict = json.loads(data)

  task = {
    "apiId": api_id,
    "build": build,
    "projectId": project_id
  }
  _get_domains_service().create_domain(data_dict["domain"], data_dict["path"], api_id)
  save_task = _get_provisioning_tasks_service().save_task(task)
  return app.response_class(response=json.dumps(save_task),
                            status=201,
                            mimetype="application/json")

@FlaskResponseGenerator()
@app.route("/v{0}/domains".format(API_MAJOR_VERSION))
def resolve_domains():
  """Returns information about the given domain and path. It first searches the list of
  platform apis and then user defined domains and apis.

  In bravehub, it is possible to have a path belonging to a domain hosted on a completely
  separated infrastructure than other paths belonging to the same domain. This is how
  micro services are expected to work.
  """

  domain = request.args.get("domain", "")
  path = request.args.get("path", "")

  platform_api = _serve_platform_api(domain)
  if platform_api:
    return platform_api

  api_id = _get_domains_service().get_api_id_for_domain_and_path(domain, path)
  if api_id:
    worker_port = _get_metaports_service().get_port_mappings(api_id)
    if worker_port:
      response = {
        "workerDomain": WORKER_DOMAIN,
        "workerPort": worker_port
      }
      return app.response_class(response=json.dumps(response),
                                status=200,
                                mimetype="application/json")

  err_msg = "Domain {0} not deployed on {1}.".format(domain, PLATFORM_SUFFIX)
  return app.response_class(response=json.dumps({"message": err_msg}),
                            status=404,
                            mimetype="application/json")
