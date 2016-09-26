FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-setuptools \
    wget \
  && wget --no-check-certificate https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64.deb \
  && dpkg -i dumb-init_1.1.3_amd64.deb \
  && rm dumb-init_*.deb \
  && apt-get clean \
  && apt-get purge -y wget \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*

COPY . /proj

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      gcc \
      git \
      libyaml-0-2 \
      libyaml-dev \
      python3-dev \
      python3-pip \
    && cd /proj/cephlcmlib \
    && pip3 install --no-cache-dir --disable-pip-version-check -r requirements.txt -c /proj/constraints.txt \
    && python3 setup.py install \
    && cd /proj/backend/common \
    && pip3 install --no-cache-dir --disable-pip-version-check -r requirements.txt -c /proj/constraints.txt \
    && python3 setup.py install \
    && cd /proj/plugins/playbook/server_discovery \
    && python3 setup.py install \
    && cd / \
    && rm -r /proj \
    && apt-get clean \
    && apt-get purge -y git libyaml-dev gcc python3-dev python3-pip \
    && apt-get autoremove -y \
    && rm -r /var/lib/apt/lists/*
