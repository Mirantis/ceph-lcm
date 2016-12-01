# vi: set ft=dockerfile :


FROM decapod-base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with plugins for Decapod" version="0.2.0" vendor="Mirantis"


COPY output/eggs /eggs


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    python3-pip \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/decapod_plugin_playbook*.whl \
  && rm -r /eggs \
  && apt-get clean \
  && apt-get purge -y python3-dev python3-pip gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*
