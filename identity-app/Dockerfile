FROM node:8.7.0-alpine

ADD .gitignore /root/.gitignore
ADD src /root/src
ADD index.html /root/index.html

ADD package.json /root/package.json
ADD polymer.json /root/polymer.json
ADD .eslintrc.json /root/.eslintrc.json

RUN apk add --no-cache git && \
    cd /root && \
    npm install -d

RUN cd /root && \
    npm run lint

RUN cd /root && \
   node_modules/.bin/polymer build

WORKDIR /root
ENTRYPOINT [ "npm", "start" ]
