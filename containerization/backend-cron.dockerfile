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


FROM decapod/controller
MAINTAINER Mirantis Inc.


LABEL version="0.2.0" description="Different cron jobs for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    cron \
    curl \
    gcc \
    git \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
  && cd /project \
  && git reset --hard \
  && echo "cron=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "cron=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip3 install --no-cache-dir --disable-pip-version-check backend/api backend/keystone_sync \
  && pip2 install --no-cache-dir --disable-pip-version-check backend/monitoring \
  && curl --silent --show-error --fail --location \
    --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" -o - \
    "https://caddyserver.com/download/build?os=linux&arch=amd64&features=" | \
    tar --no-same-owner -C /usr/bin/ -xz caddy \
  && chmod 0755 /usr/bin/caddy \
  && mkdir -p /www \
  && cat containerization/files/crontab | crontab - \
  && mkdir -p /etc/caddy \
  && mv containerization/files/cron-caddyfile /etc/caddy/config \
  && mkfifo /var/log/cron.log \
  && cd / \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y git gcc python3-pip python3-dev python-dev python-pip curl \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000

CMD ["dockerize", "-wait", "tcp://database:27017", "--", "sh", "-c", "caddy -conf '/etc/caddy/config' & cron && tail -F /var/log/cron.log"]
