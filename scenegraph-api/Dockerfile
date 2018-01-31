FROM alpine:3.6
USER root
EXPOSE 5000

ADD scenegraph-api/src /root/scenegraph-api/src
ADD bravehub_shared /root/scenegraph-api/src/bravehub_shared
ADD scenegraph-api/requirements.txt /root/scenegraph-api/requirements.txt
RUN cd /root/scenegraph-api && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    pip3 install -r requirements.txt && \
    pip3 install -r src/bravehub_shared/requirements.txt && \
    apk del python3-dev gcc musl-dev

WORKDIR /root/scenegraph-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
