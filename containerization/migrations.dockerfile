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


LABEL version="0.2.0" description="Migration script for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=

ENV DEBIAN_FRONTEND=noninteractive


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libffi-dev \
    python3-dev \
    python3-pip \
  && cd /project \
  && git reset --hard \
  && echo "migrations=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "migrations=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip3 install --no-cache-dir --disable-pip-version-check \
    backend/api \
    backend/controller \
    backend/migration \
  && cd / \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y git libffi-dev python3-pip python3-dev gcc \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-migrations"]
