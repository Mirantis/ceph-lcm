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


FROM docker-prod-virtual.docker.mirantis.net/ubuntu:xenial
MAINTAINER Mirantis Inc.


LABEL version="1.0.0" description="Image to run UI tests" vendor="Mirantis"


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
    curl \
    firefox \
    xvfb \
    xz-utils \
  && curl -sfL -o - https://nodejs.org/dist/v6.9.5/node-v6.9.5-linux-x64.tar.xz \
     | tar --no-same-owner --strip-components 1 -C /usr/local -xJ \
  && npm install -g karma \
  && npm cache clean \
  && apt-get purge -y curl xz-utils \
  && apt-get clean \
  && apt-get autoremove -y --purge \
  && rm -r /var/lib/apt/lists/* \
  && echo '#!/bin/bash' > /entrypoint.sh \
  && echo 'Xvfb :1 -screen 0 1600x1200x16 & exec "$@"' >> /entrypoint.sh \
  && chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]
