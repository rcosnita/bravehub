FROM bravehub_hbase-regionserver-1.api.internal.bravehub-dev.com:latest

USER root
RUN cd /root && \
    echo "export JAVA_HOME=/usr/lib/jvm/default-jvm" >> "/root/.bashrc"

WORKDIR /root/hbase
ENTRYPOINT source ~/.bashrc && \
    echo ${HBASE_SITE_CONFIG} | base64 -d > conf/hbase-site.xml && \
    sleep 10 && \
    bin/hbase shell ${SCRIPT_NAME}
