FROM bravehub/hbase:0.1.0

USER root
ADD scripts /root/scripts
RUN cd /root && \
    echo "export JAVA_HOME=/usr/lib/jvm/default-jvm" >> "/root/.bashrc"

WORKDIR /root/hbase
ENTRYPOINT source ~/.bashrc && \
    echo ${HBASE_SITE_CONFIG} | base64 -d > conf/hbase-site.xml && \
    sleep 10 && \
    bin/hbase shell ${SCRIPT_NAME}
