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


LABEL version="1.0.1" description="API service for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


HEALTHCHECK --interval=30s --timeout=20s CMD \
  decapod-healthcheck-db \
  && decapod-healthcheck-api 127.0.0.1 8000


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libffi-dev \
    libpcre3 \
    libpcre3-dev \
    python3-dev \
    python3-pip \
  && cd /project \
  && git reset --hard \
  && echo "api=$(git rev-parse HEAD)" >> /etc/git-release \
  && cp containerization/files/uwsgi.ini /etc/decapod-api-uwsgi.ini \
  && echo "api=$(scd -s git_pep440 -p)" >> /etc/decapod-release \
  && scd -s git_pep440 -v \
  && pip3 install --no-cache-dir --disable-pip-version-check -c constraints.txt uwsgi \
  && pip3 install --no-cache-dir --disable-pip-version-check backend/api[keystone] \
  && cd / \
  && rm -r /project \
  && pip3 --no-cache-dir --disable-pip-version-check freeze > packages-python3 \
  && apt-get clean \
  && apt-get purge -y git libffi-dev libpcre3-dev python3-dev python3-pip gcc \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000

ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "uwsgi", "/etc/decapod-api-uwsgi.ini"]
