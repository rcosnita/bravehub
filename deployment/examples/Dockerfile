FROM alpine:3.6

ADD requirements.txt /root/requirements.txt
RUN cd /root && \
    apk add --no-cache python3 python3-dev alpine-sdk && \
    pip3 install -r requirements.txt && \
    apk del python3-dev alpine-sdk

WORKDIR /root
ENTRYPOINT sleep ${DELAYED_START_MS:-0} && \
    python3 python/happybase-sample.py
