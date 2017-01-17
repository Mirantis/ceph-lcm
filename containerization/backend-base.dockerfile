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


LABEL version="0.2.0" description="Base image of Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=

ENV DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 LANG=C.UTF-8 PIP_INDEX_URL=${pip_index_url:-https://pypi.python.org/simple/}


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
  && apt-get clean \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


COPY .git            /project/.git
COPY ubuntu_apt.list /etc/apt/sources.list


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    libffi6 \
    libffi-dev \
    libpython3.5 \
    libssl1.0.0 \
    libssl-dev \
    libyaml-0-2 \
    libyaml-dev \
    python3 \
    python3-dev \
    python3-pip \
    git \
    wget \
  && pip3 --no-cache-dir --disable-pip-version-check install 'setuptools==32.3.1' \
  && cd /project \
  && git reset --hard \
  && echo "base=$(git rev-parse HEAD)" > /etc/git-release \
  && mkdir -p /etc/decapod \
  && cp containerization/files/devconfigs/config.yaml /etc/decapod/config.yaml \
  && wget --no-check-certificate https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb \
  && dpkg -i dumb-init_1.2.0_amd64.deb \
  && rm dumb-init_*.deb \
  && wget --no-check-certificate https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz \
  && pip3 --no-cache-dir --disable-pip-version-check install 'scd[yaml]~=1.2' \
  && echo "base=$(scd -s git_pep440 -p)" > /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip3 --no-cache-dir --disable-pip-version-check install \
    backend/common \
    backend/docker \
    plugins/alerts/emails \
    plugins/playbook/server_discovery \
  && apt-get clean \
  && apt-get purge -y git wget libffi-dev libssl-dev libyaml-dev gcc python3-dev python3-pip \
  && apt-get autoremove --purge -y \
  && cd / \
  && rm -r /project \
  && rm -r /var/lib/apt/lists/*
