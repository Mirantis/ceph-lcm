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
    \
    # workaround for https://github.com/pypa/pip/issues/4180
  && ln -s /project/.git /tmp/.git && ln -s /project/.git /.git \
  && cd /project \
  && git reset --hard \
  && git submodule update --init --recursive \
  && scd -v \
  && pip3 install --no-cache-dir \
    /project/plugins/playbook/add_mon \
    /project/plugins/playbook/add_osd \
    /project/plugins/playbook/deploy_cluster \
    /project/plugins/playbook/purge_cluster \
    /project/plugins/playbook/remove_osd \
    /project/plugins/playbook/telegraf_integration \
  && rm -r /project /tmp/.git /.git \
  && apt-get clean \
  && apt-get purge -y git python3-dev python3-pip gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*
