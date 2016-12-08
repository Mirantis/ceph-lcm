# vi: set ft=dockerfile :


FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image of Decapod" version="0.2.0" vendor="Mirantis"

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    libffi6 \
    libpython3.5 \
    libssl1.0.0 \
    libyaml-0-2 \
    python3.5 \
    python3-setuptools \
    wget \
  && wget --no-check-certificate https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb \
  && dpkg -i dumb-init_1.2.0_amd64.deb \
  && rm dumb-init_*.deb \
  && wget --no-check-certificate https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz \
  && apt-get clean \
  && apt-get purge -y wget \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


COPY backend/common                    /project/common
COPY backend/docker                    /project/docker
COPY decapodlib                        /project/decapodlib
COPY plugins/playbook/server_discovery /project/server_discovery
COPY plugins/alerts/emails             /project/emails
COPY config.yaml                       /etc/decapod/config.yaml


RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      gcc \
      libffi-dev \
      libssl-dev \
      libyaml-dev \
      python3-dev \
      python3-pip \
    && pip3 install --compile --no-cache-dir --disable-pip-version-check /project/* \
    && apt-get clean \
    && apt-get purge -y libffi-dev libssl-dev libyaml-dev gcc python3-dev python3-pip \
    && apt-get autoremove -y \
    && rm -r /project \
    && rm -r /var/lib/apt/lists/*
