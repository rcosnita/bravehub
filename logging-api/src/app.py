from flask import Flask
import json

app = Flask(__name__)

@app.route("/")
def hello():
  return json.dumps({
    "api_name": "logging-api:0.0.1",
    "api_version": {
      "major": 0,
      "minor": 1,
      "patch": 0
    }
  })
