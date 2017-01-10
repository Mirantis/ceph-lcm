# vi: set ft=dockerfile :


FROM docker-prod-virtual.docker.mirantis.net/nginx:stable
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Base image with frontend for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=

ENV NPM_CONFIG_REGISTRY=${npm_registry:-https://registry.npmjs.org/} DEBIAN_FRONTEND=noninteractive


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
  && apt-get install -y --no-install-recommends wget xz-utils git \
  && wget https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz \
  && wget https://nodejs.org/dist/v6.9.4/node-v6.9.4-linux-x64.tar.xz \
  && tar xf node-v6.9.4-linux-x64.tar.xz \
  && mkdir -p /static /ssl /etc/nginx \
  && cd /project \
  && git reset --hard \
  && echo "frontend=$(git rev-parse HEAD)" > /etc/git-release \
  && cp containerization/files/devconfigs/nginx-dhparam.pem /ssl/dhparam.pem \
  && cp containerization/files/devconfigs/nginx-selfsigned.crt /ssl/ssl.crt \
  && cp containerization/files/devconfigs/nginx-selfsigned.key /ssl/ssl.key \
  && cp containerization/files/nginx.conf /etc/nginx/nginx.conf \
  && cd /project/ui \
  && PATH=/node-v6.9.4-linux-x64/bin:$PATH sh -c 'npm install && npm run build && npm cache clean' \
  && mv build/* /static \
  && cd / \
  && apt-get purge -y wget xz-utils git \
  && apt-get clean \
  && apt-get autoremove --purge -y \
  && rm -r /project /var/lib/apt/lists/* /node-v6.9.4-linux*


CMD ["dockerize", "-wait", "tcp://api:8000", "--", "nginx", "-g", "daemon off;"]
