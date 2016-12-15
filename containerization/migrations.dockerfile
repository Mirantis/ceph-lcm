# vi: set ft=dockerfile :



FROM decapod-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Migration script for Decapod" version="0.2.0" vendor="Mirantis"


COPY backend/api        /project/api
COPY backend/controller /project/controller
COPY backend/migration  /project/migration
COPY .git               /.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libffi-dev \
    python3-dev \
    python3-pip \
    \
    # workaround for https://github.com/pypa/pip/issues/4180
  && ln -s /project/.git /tmp/.git && ln -s /project/.git /.git \
  && pip3 install --no-cache-dir /project/* \
  && rm -r /project /.git /tmp/.git \
  && apt-get clean \
  && apt-get purge -y git libffi-dev python3-pip python3-dev gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-migrations"]
