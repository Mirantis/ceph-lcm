# vi: set ft=dockerfile :


FROM docker-prod-virtual.docker.mirantis.net/ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Image to run UI tests" vendor="Mirantis"


ARG pip_index_url=
ARG npm_registry_url=
ENV NPM_CONFIG_REGISTRY=${npm_registry:-https://registry.npmjs.org/} DISPLAY=:1.0 DEBIAN_FRONTEND=noninteractive


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
  && apt-get clean \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


COPY ubuntu_apt.list /etc/apt/sources.list


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    firefox \
    nodejs \
    nodejs-legacy \
    npm \
    xvfb \
  && npm install -g karma \
  && npm cache clean \
  && apt-get clean \
  && apt-get autoremove -y --purge \
  && rm -r /var/lib/apt/lists/* \
  && echo '#!/bin/bash' > /entrypoint.sh \
  && echo 'Xvfb :1 -screen 0 1600x1200x16 & exec "$@"' >> /entrypoint.sh \
  && chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]
