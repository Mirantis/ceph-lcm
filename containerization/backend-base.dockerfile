# vi: set ft=dockerfile :


FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY containerization/files/sources.list /etc/apt/sources.list


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    libffi6 \
    libpython3.5 \
    libyaml-0-2 \
    python3.5 \
    python3-setuptools \
    wget \
  && wget --no-check-certificate https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb \
  && dpkg -i dumb-init_1.2.0_amd64.deb \
  && rm dumb-init_*.deb \
  && apt-get clean \
  && apt-get purge -y wget \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


COPY output/eggs /eggs
COPY config.yaml /etc/cephlcm/config.yaml


RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      gcc \
      libffi-dev \
      libyaml-dev \
      python3-dev \
      python3-pip \
    && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcmlib*.whl \
    && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcm_common*.whl \
    && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcm_plugin_server_discovery*.whl \
    && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcm_plugin_alerts*.whl \
    && rm -r /eggs \
    && apt-get clean \
    && apt-get purge -y libffi-dev libyaml-dev gcc python3-dev python3-pip \
    && apt-get autoremove -y \
    && rm -r /var/lib/apt/lists/*
