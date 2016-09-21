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
  && rm -rf /var/lib/apt/lists/*

COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY backend/common/requirements.txt /common-requirements.txt
COPY cephlcmlib/requirements.txt /cephlcmlib-requirements.txt

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      gcc \
      libyaml-0-2 \
      libyaml-dev \
      python3-dev \
      python3-pip \
    && pip3 install --no-cache-dir --disable-pip-version-check \
      -c /constraints.txt \
      -r /cephlcmlib-requirements.txt \
      /eggs/cephlcmlib*.tar.gz \
    && pip3 install --no-cache-dir --disable-pip-version-check \
      -c /constraints.txt \
      -r /common-requirements.txt \
      /eggs/cephlcm_common*.tar.gz \
    && rm -r /common-requirements.txt /cephlcmlib-requirements.txt /constraints.txt /eggs \
    && apt-get clean \
    && apt-get purge -y libyaml-dev gcc python3-dev python3-pip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
