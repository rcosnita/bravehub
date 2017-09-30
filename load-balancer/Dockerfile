FROM alpine:3.6
EXPOSE 8080

USER root

ADD src /root/bravehub-router
ADD third-party /root/third-party
RUN apk add --no-cache alpine-sdk pcre-dev openssl-dev libxml2-dev libxslt-dev gd-dev geoip-dev cmake && \
    cd /root && \
    git clone https://github.com/nginx/nginx.git && \
    cd nginx && \
    git checkout tags/release-1.13.5 && \
    CFLAGS="-fPIC" ./auto/configure --prefix=/etc/nginx \
        --sbin-path=/usr/sbin/nginx \
        --modules-path=/usr/lib/nginx/modules \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --http-log-path=/var/log/nginx/access.log \
        --pid-path=/var/run/nginx.pid \
        --lock-path=/var/run/nginx.lock \
        --http-client-body-temp-path=/var/cache/nginx/client_temp \
        --http-proxy-temp-path=/var/cache/nginx/proxy_temp \
        --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
        --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp \
        --http-scgi-temp-path=/var/cache/nginx/scgi_temp \
        --user=nginx --group=nginx \
        --with-http_ssl_module \
        --with-http_realip_module \
        --with-http_addition_module \
        --with-http_sub_module \
        --with-http_dav_module \
        --with-http_flv_module \
        --with-http_mp4_module \
        --with-http_gunzip_module \
        --with-http_gzip_static_module \
        --with-http_random_index_module \
        --with-http_secure_link_module \
        --with-http_stub_status_module \
        --with-http_auth_request_module \
        --with-http_xslt_module=dynamic \
        --with-http_image_filter_module=dynamic \
        --with-http_geoip_module=dynamic \
        --with-threads \
        --with-stream \
        --with-stream_ssl_module \
        --with-stream_ssl_preread_module \
        --with-stream_realip_module \
        --with-stream_geoip_module=dynamic \
        --with-http_slice_module \
        --with-mail \
        --with-mail_ssl_module \
        --with-compat \
        --with-http_v2_module \
        --add-dynamic-module=/root/bravehub-router && \
    mkdir -p /root/bravehub-router/build || true && \
    cd /root/bravehub-router/build && \
    cmake ../ && \
    make -j4 && \
    cp libbravehub-router.so /usr/local/lib && \
    cd /root/nginx && \
    make -j8 && \
    make install && \
    adduser -h /home/nginx -D -H nginx && \
    mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx/client_temp && \
    ln -s /usr/lib/nginx/modules /etc/nginx/modules

WORKDIR /root
ENTRYPOINT /usr/sbin/nginx
