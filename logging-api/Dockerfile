FROM alpine:3.6
USER root
EXPOSE 5000

ADD logging-api/src /root/logging-api/src
ADD bravehub_shared /root/logging-api/src/bravehub_shared
ADD logging-api/requirements.txt /root/logging-api/requirements.txt
RUN cd /root/logging-api && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    pip3 install -r requirements.txt && \
    pip3 install -r src/bravehub_shared/requirements.txt && \
    apk del python3-dev gcc musl-dev

WORKDIR /root/logging-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
