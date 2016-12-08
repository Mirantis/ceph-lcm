# vi: set ft=dockerfile :


FROM decapod-base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with plugins for Decapod" version="0.2.0" vendor="Mirantis"


COPY plugins/playbook/add_mon        /project/add_mon
COPY plugins/playbook/add_osd        /project/add_osd
COPY plugins/playbook/deploy_cluster /project/deploy_cluster
COPY plugins/playbook/purge_cluster  /project/purge_cluster
COPY plugins/playbook/remove_osd     /project/remove_osd


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    python3-pip \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /project/* \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y python3-dev python3-pip gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*
