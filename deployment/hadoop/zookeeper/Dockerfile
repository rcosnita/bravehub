FROM alpine:3.6

USER root
EXPOSE 2181

RUN cd /root && \
    apk add --no-cache openjdk8-jre-base wget bash && \
    wget http://mirror.evowise.com/apache/zookeeper/zookeeper-3.4.11/zookeeper-3.4.11.tar.gz && \
    tar xzvf zookeeper-3.4.11.tar.gz && \
    rm zookeeper-3.4.11.tar.gz && \
    apk del wget && \
    ln -s zookeeper-3.4.11 zookeeper

WORKDIR /root
ENTRYPOINT export JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk && \
    export PATH=$PATH:$JAVA_HOME/bin && \
    echo ${ZOOKEEPER_CONFIG} | base64 -d > zookeeper/conf/zoo.cfg && \
    ./zookeeper/bin/zkServer.sh start-foreground
