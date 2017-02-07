# vi: set ft=dockerfile :
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM decapod/base-plugins
MAINTAINER Mirantis Inc.


LABEL version="0.2.0" description="Controller service for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libffi-dev \
    libpython2.7 \
    libssl-dev \
    openssh-client \
    python2.7 \
    python3-apt \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    python-setuptools \
  && mkdir -p /root/.ssh \
  && chmod 700 /root/.ssh \
  && cd /project \
  && git reset --hard \
  && git submodule update --init --recursive \
  && echo "controller=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "controller=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip2 install --no-cache-dir --disable-pip-version-check --upgrade 'setuptools==32.3.1' \
  && pip2 install --no-cache-dir --disable-pip-version-check backend/ansible \
  && pip3 install --no-cache-dir --disable-pip-version-check --process-dependency-links backend/controller \
  && cp containerization/files/devconfigs/ansible_ssh_keyfile.pem /root/.ssh/id_rsa \
  && chmod 0600 /root/.ssh/id_rsa \
  && /usr/local/bin/decapod-ansible-deploy-config \
  && cd / \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y git libssl-dev libffi-dev python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-controller"]
