# vi: set ft=dockerfile :



FROM decapod-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Migration script for Decapod" version="0.2.0" vendor="Mirantis"


COPY backend/migration  /project/migration
COPY backend/api        /project/api
COPY backend/controller /project/controller


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
      gcc \
      libffi-dev \
      python3-dev \
      python3-pip \
  && pip3 install --no-cache-dir /project/* \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y libffi-dev python3-pip python3-dev gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-migrations"]
