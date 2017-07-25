from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
  return "configuration-api:0.0.1"
