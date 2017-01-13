# vi: set ft=dockerfile :


FROM decapod/base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Base image with plugins for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    git \
    python3-dev \
    python3-pip \
  && cd /project \
  && git reset --hard \
  && git submodule update --init --recursive \
  && echo "plugins=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "plugins=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip3 install --no-cache-dir --disable-pip-version-check \
    plugins/playbook/add_mon \
    plugins/playbook/add_osd \
    plugins/playbook/deploy_cluster \
    plugins/playbook/purge_cluster \
    plugins/playbook/remove_osd \
    plugins/playbook/telegraf_integration \
  && cd / \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y git python3-dev python3-pip gcc \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*
