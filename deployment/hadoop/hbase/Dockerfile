FROM alpine:3.6

USER root
RUN cd /root && \
    apk add --no-cache openjdk8-jre-base wget bash && \
    wget http://www-eu.apache.org/dist/hbase/1.3.1/hbase-1.3.1-bin.tar.gz && \
    tar -xzvf hbase-1.3.1-bin.tar.gz && \
    rm hbase-1.3.1-bin.tar.gz && \
    ln -s hbase-1.3.1 hbase && \
    apk del wget

WORKDIR /root/hbase
ENTRYPOINT export JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk && \
    export PATH=$PATH:$JAVA_HOME/bin && \
    echo ${HBASE_SITE_CONFIG} | base64 -d > conf/hbase-site.xml && \
    echo ${HBASE_RS_CONFIG} | base64 -d > conf/regionservers && \
    sed -i "s@{{hbase.regionserver.hostname}}@$(hostname)@" conf/hbase-site.xml && \
    ${HBASE_CMD}
