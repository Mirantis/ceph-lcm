# vi: set ft=dockerfile :


FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image of Decapod" version="0.2.0" vendor="Mirantis"

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8


COPY backend/common                                          /project/backend/common
COPY backend/docker                                          /project/backend/docker
COPY config.yaml                                             /etc/decapod/config.yaml
COPY containerization/files/package_managers/pip.conf        /root/.config/pip/pip.conf
COPY containerization/files/package_managers/ubuntu_apt.list /etc/apt/sources.list
COPY decapodlib                                              /project/decapodlib
COPY .git                                                    /project/.git
COPY plugins/alerts/emails                                   /project/plugins/alerts/emails
COPY plugins/playbook/server_discovery                       /project/plugins/playbook/server_discovery


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
    \
    # workaround for https://github.com/pypa/pip/issues/4180
  && ln -s /project/.git /tmp/.git \
  && wget --no-check-certificate https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb \
  && dpkg -i dumb-init_1.2.0_amd64.deb \
  && rm dumb-init_*.deb \
  && wget --no-check-certificate https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz
RUN pip3 --no-cache-dir install \
    /project/decapodlib \
    /project/backend/* \
    /project/plugins/alerts/* \
    /project/plugins/playbook/* \
  && apt-get clean \
  && apt-get purge -y git wget libffi-dev libssl-dev libyaml-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /project /tmp/.git .git \
  && rm -r /var/lib/apt/lists/*
