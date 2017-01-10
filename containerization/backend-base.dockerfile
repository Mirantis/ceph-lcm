# vi: set ft=dockerfile :


FROM docker-prod-virtual.docker.mirantis.net/ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


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
    python3.5 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    git \
    wget \
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
  && pip3 --no-cache-dir --disable-pip-version-check install 'scd[yaml]~=1.1' \
  && echo "base=$(scd -p)" > /etc/decapod-release \
  && scd -v \
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
