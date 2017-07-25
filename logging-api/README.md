# Getting started

## Running without docker

```sh
python3 -m venv logging-api-env
source logging-api-env/bin/activate
pip install -r requirements.txt
FLASK_APP=src/app.py flask run --host=0.0.0.0
```

## Running with docker

```sh
docker build -t bravehub/logging-api:0.0.1 -f Dockerfile .
docker run --rm -it -p 0.0.0.0:5010:5000/tcp bravehub/logging-api:0.0.1
```
