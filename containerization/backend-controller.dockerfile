# vi: set ft=dockerfile :


FROM decapod/base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


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
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    python-setuptools \
  && mkdir -p /root/.ssh \
  && cd /project \
  && git reset --hard \
  && git submodule update --init --recursive \
  && echo "controller=$(git rev-parse HEAD)" >> /etc/git-release \
  && echo "controller=$(scd -p)" >> /etc/decapod-release \
  && scd -v \
  && pip2 install --no-cache-dir --disable-pip-version-check --upgrade 'setuptools>=26' \
  && pip2 install --no-cache-dir --disable-pip-version-check backend/ansible \
  && pip3 install --no-cache-dir --disable-pip-version-check backend/controller \
  && /usr/local/bin/decapod-ansible-deploy-config \
  && cd / \
  && rm -r /project \
  && chmod 700 /root/.ssh/ \
  && apt-get clean \
  && apt-get purge -y git libssl-dev libffi-dev python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove --purge -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-controller"]
