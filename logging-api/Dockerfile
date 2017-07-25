FROM alpine:3.6
USER root
EXPOSE 5000

ADD src /root/logging-api/src
ADD requirements.txt /root/logging-api/requirements.txt
RUN cd /root/logging-api && \
    apk add --no-cache python3 && \
    pip3 install -r requirements.txt
WORKDIR /root/logging-api
ENTRYPOINT FLASK_APP=src/app.py flask run --host=0.0.0.0
