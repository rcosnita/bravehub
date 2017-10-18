import json
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
  return "provisioning-api:0.0.1"

@app.route("/v1/domains")
def resolve_domains():
  body = json.dumps({
    # "workerDomain": "tomcat-sample-app.internal.bravehub-dev.com",
    # "workerPort": 8080
    "workerDomain": "192.168.128.1",
    "workerPort": 10000
  })

  return app.response_class(response=body,
                            status=200,
                            mimetype="application/json")
