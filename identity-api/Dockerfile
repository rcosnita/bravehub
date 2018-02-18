FROM alpine:3.6
USER root
EXPOSE 5040

ADD identity-api/src /root/identity-api/src
ADD bravehub_shared /root/identity-api/src/bravehub_shared
ADD identity-api/requirements.txt /root/identity-api/requirements.txt
RUN cd /root/identity-api && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    pip3 install -r requirements.txt && \
    pip3 install -r src/bravehub_shared/requirements.txt && \
    apk del python3-dev gcc musl-dev

WORKDIR /root/identity-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
