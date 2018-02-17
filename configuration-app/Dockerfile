FROM node:8.7.0-alpine

ADD .gitignore /root/.gitignore
ADD src /root/src
ADD images /root/images
ADD index.html /root/index.html
ADD service-worker.js /root/service-worker.js
ADD sw-precache-config.js /root/sw-precache-config.js

ADD package.json /root/package.json
ADD polymer.json /root/polymer.json
ADD bower.json /root/bower.json
ADD manifest.json /root/manifest.json
ADD .eslintrc.json /root/.eslintrc.json
ADD third-party /root/third-party

RUN apk add --no-cache git && \
    git config --global url.https://github.com/.insteadOf git://github.com/ && \
    cd /root && \
    npm install -d && \
    npm install -d bower && \
    node_modules/.bin/bower install --allow-root -d

RUN cd /root && \
    npm run lint

RUN cd /root && \
   sed s/localhost:5000/configuration-api.api.bravehub-dev.com/g /root/src/js/constants.js.tpl > /root/src/js/constants.js && \
   node_modules/.bin/polymer build

WORKDIR /root
ENTRYPOINT [ "npm", "start" ]
