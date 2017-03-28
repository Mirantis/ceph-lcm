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


FROM decapod/base
MAINTAINER Mirantis Inc.


LABEL version="1.1.0" description="Admin utilities for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=
ENV DECAPOD_URL=http://frontend:80 DECAPOD_LOGIN=root DECAPOD_PASSWORD=root EDITOR=vim


HEALTHCHECK --interval=30s --timeout=20s CMD \
  decapod-healthcheck-db \
  && decapod-healthcheck-process cron \
  && decapod-healthcheck-ansible \
  && curl-healthcheck 200 http://127.0.0.1:8000 '--user root:r00tme' \
  && curl-healthcheck 200 http://127.0.0.1:8001


COPY .git /project/.git


RUN set -x \
  && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 \
  && echo "deb [arch=amd64] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" > /etc/apt/sources.list.d/mongodb.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    cron \
    curl \
    g++ \
    gcc \
    git \
    jq \
    jshon \
    less \
    libapt-pkg-dev \
    libffi-dev \
    libpython2.7 \
    libssl-dev \
    libtool \
    make \
    mongodb-org-tools \
    nano \
    openssh-client \
    python2.7 \
    python3-apt \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    python-setuptools \
    tox \
    vim \
  && cd /project \
  && git reset --hard \
  && git submodule update --init --recursive \
  && echo "admin=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "admin=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && install containerization/files/curl-healthcheck.sh /usr/local/bin/curl-healthcheck \
  && scd -s git_pep440 -v \
  && pip2 install --no-cache-dir --disable-pip-version-check --upgrade 'setuptools==32.3.1' \
  && pip2 install --no-cache-dir --disable-pip-version-check \
    ./backend/ansible \
    ./backend/monitoring \
  && pip3 install --no-cache-dir --disable-pip-version-check \
    ./decapodlib \
    ./decapodcli[color,jq,yaql,jmespath] \
    ./backend/api[keystone] \
    ./backend/controller[libapt] \
    ./backend/admin[uvloop] \
    jmespath-terminal \
  && /usr/local/bin/decapod-ansible-deploy-config \
  && _DECAPOD_ADMIN_COMPLETE=source decapod-admin >> /root/.bashrc || true \
  && _DECAPOD_COMPLETE=source decapod >> /root/.bashrc || true \
  && cp ./containerization/files/decapod-admin-dockerize.sh /usr/local/bin/decapod-admin-wait \
  && cp ./containerization/files/decapod-dockerize.sh /usr/local/bin/decapod-wait \
  && ln -s /usr/local/bin/decapod /usr/local/bin/cli \
  && ln -s /usr/local/bin/decapod-wait /usr/local/bin/cli-wait \
  && ln -s /usr/local/bin/decapod-admin /usr/local/bin/admin \
  && ln -s /usr/local/bin/decapod-admin-wait /usr/local/bin/admin-wait \
  && cp ./scripts/debug_snapshot.py /debug-snapshot \
  && curl --silent --show-error --fail --location \
    --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" -o - \
    "https://caddyserver.com/download/build?os=linux&arch=amd64&features=" | \
    tar --no-same-owner -C /usr/bin/ -xz caddy \
  && curl --silent --show-error --fail --location -o /usr/local/bin/jp https://github.com/jmespath/jp/releases/download/0.1.2/jp-linux-amd64 \
  && chmod +x /usr/local/bin/jp \
  && chmod 0755 /usr/bin/caddy \
  && mkdir -p /www/monitoring /www/docs \
  && locale-gen "en_US.UTF-8" \
  && cd /project \
  && tox -v -e docs \
  && mv docs/build/html/* /www/docs \
  && cat containerization/files/crontab | crontab - \
  && mkdir -p /etc/caddy \
  && mv containerization/files/cron-caddyfile /etc/caddy/config \
  && mkfifo /var/log/cron.log \
  && cd / \
  && rm -r /project /root/.cache/pip \
  && apt-key del 0C49F3730359A14518585931BC711F9BA15703C6 \
  && rm /etc/apt/sources.list.d/mongodb.list \
  && pip3 --no-cache-dir --disable-pip-version-check freeze > packages-python3 \
  && pip2 --no-cache-dir --disable-pip-version-check freeze > packages-python2 \
  && apt-get clean \
  && apt-get purge -y \
    autoconf \
    automake \
    g++ \
    gcc \
    git \
    libapt-pkg-dev \
    libffi-dev \
    libssl-dev \
    libtool \
    make \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    tox \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000 8001


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "sh", "-c", "caddy -conf /etc/caddy/config & cron & tail -F /var/log/cron.log"]
