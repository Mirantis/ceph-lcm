# vi: set ft=dockerfile :
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM docker-prod-virtual.docker.mirantis.net/nginx:stable
MAINTAINER Mirantis Inc.


LABEL version="1.2.0" description="Base image with frontend for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=

ENV NPM_CONFIG_REGISTRY=${npm_registry:-https://registry.npmjs.org/} DEBIAN_FRONTEND=noninteractive


HEALTHCHECK --interval=30s --timeout=20s CMD \
  curl-healthcheck    200 http://127.0.0.1:80 \
  && curl-healthcheck 200 http://127.0.0.1:80/v1/info/ \
  && curl-healthcheck 200 https://127.0.0.1:443 \
  && curl-healthcheck 200 https://127.0.0.1:443/v1/info/


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
  && apt-get clean \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


COPY debian_apt.list /etc/apt/sources.list
COPY .git            /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends curl wget xz-utils git \
  && wget https://github.com/jwilder/dockerize/releases/download/v0.4.0/dockerize-linux-amd64-v0.4.0.tar.gz \
  && tar -C /usr/local/bin -xzf dockerize-linux-amd64-v0.4.0.tar.gz \
  && rm dockerize-linux-amd64-v0.4.0.tar.gz \
  && wget https://nodejs.org/dist/v6.9.4/node-v6.9.4-linux-x64.tar.xz \
  && tar xf node-v6.9.4-linux-x64.tar.xz \
  && mkdir -p /static /ssl /etc/nginx \
  && cd /project \
  && git reset --hard \
  && echo "frontend=$(git rev-parse HEAD)" > /etc/git-release \
  && install containerization/files/curl-healthcheck.sh /usr/local/bin/curl-healthcheck \
  && cp containerization/files/devconfigs/nginx-dhparam.pem /ssl/dhparam.pem \
  && cp containerization/files/devconfigs/nginx-selfsigned.crt /ssl/ssl.crt \
  && cp containerization/files/devconfigs/nginx-selfsigned.key /ssl/ssl.key \
  && cp containerization/files/nginx.conf /etc/nginx/nginx.conf \
  && cd /project/ui \
  && PATH=/node-v6.9.4-linux-x64/bin:$PATH sh -c 'npm install && npm run build && npm cache clean' \
  && PATH=/node-v6.9.4-linux-x64/bin:$PATH npm shrinkwrap --dev \
  && mv npm-shrinkwrap.json /packages-npm \
  && mv build/* /static \
  && cd / \
  && apt-get purge -y wget xz-utils git \
  && apt-get clean \
  && apt-get autoremove --purge -y \
  && rm -r /project /var/lib/apt/lists/* /node-v6.9.4-linux*


CMD ["dockerize", "-wait", "tcp://api:8000", "--", "nginx", "-g", "daemon off;"]
