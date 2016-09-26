FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Install Python3 and dependencies
RUN set -x \
    && apt update \
    && apt install -y \
      ansible \
      g++ \
      gcc \
      git \
      pkg-config \
      python \
      python3 \
      python3-cherrypy3 \
      python3-dev \
      python3-pip \
      python-pip \
      wget \
    && wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 \
    && chmod +x /usr/local/bin/dumb-init \
    && mkdir /project \
    && apt-get clean \
    && pip2 install pymongo==3.3.0 \
    && rm -rf /var/lib/apt/lists/*

COPY . /project

RUN set -x \
    && pip3 install -U pip setuptools \
    && cd /project/backend/common && pip3 install -c /project/constraints.txt /project/backend/common \
    && cd /project/backend/common && pip3 install -c /project/constraints.txt /project/backend/api \
    && cd /project/backend/common && pip3 install -c /project/constraints.txt /project/backend/controller \
    && cd /project/backend/common && pip3 install -c /project/constraints.txt /project/plugins/playbook/server_discovery \
    && cd /project/backend/common && pip3 install -c /project/constraints.txt /project/plugins/playbook/playbook_helloworld \
    && mkdir -p /usr/share/ansible/plugins/callback \
    && cp /project/backend/controller/ansible_execution_step_callback/* /usr/share/ansible/plugins/callback \
    && mkdir -p /etc/ansible \
    && cp /project/devenv/devstage/ansible.cfg /etc/ansible \
    && mkdir -p /etc/cephlcm \
    && cp /project/devenv/devstage/config.toml /etc/cephlcm \
    && cp /project/devenv/devstage/cephlcm-api /usr/bin/cephlcm-api \
    && chmod +x /usr/bin/cephlcm-api \
    && rm -rf /project

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/dumb-init", "-c", "--"]
