# vi: set ft=dockerfile :


FROM decapod/base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="API service for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


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
  && pip3 install --no-cache-dir --disable-pip-version-check backend/api \
  && cd / \
  && rm -r /project \
  && apt-get clean \
  && apt-get purge -y git libffi-dev libpcre3-dev python3-dev python3-pip gcc \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000

ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "uwsgi", "/etc/decapod-api-uwsgi.ini"]
