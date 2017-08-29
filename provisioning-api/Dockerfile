FROM alpine:3.6
USER root
EXPOSE 5000

ADD provisioning-api/src /root/provisioning-api/src
ADD bravehub_shared /root/provisioning-api/src/bravehub_shared
ADD provisioning-api/requirements.txt /root/provisioning-api/requirements.txt
RUN cd /root/provisioning-api && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    pip3 install -r requirements.txt && \
    pip3 install -r src/bravehub_shared/requirements.txt && \
    apk del python3-dev gcc musl-dev

WORKDIR /root/provisioning-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
