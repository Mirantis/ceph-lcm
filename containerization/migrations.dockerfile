# vi: set ft=dockerfile :



FROM decapod/base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


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
