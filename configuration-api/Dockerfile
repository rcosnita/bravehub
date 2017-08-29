FROM alpine:3.6
USER root
EXPOSE 5000

ADD configuration-api/src /root/configuration-api/src
ADD bravehub_shared /root/configuration-api/src/bravehub_shared
ADD configuration-api/requirements.txt /root/configuration-api/requirements.txt
RUN cd /root/configuration-api && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    pip3 install -r requirements.txt && \
    pip3 install -r src/bravehub_shared/requirements.txt && \
    apk del python3-dev gcc musl-dev

WORKDIR /root/configuration-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
