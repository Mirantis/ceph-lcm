# vi: set ft=dockerfile :


FROM decapod-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Controller service for Decapod" vendor="Mirantis"


COPY ansible_ssh_keyfile.pem /root/.ssh/id_rsa
COPY backend/ansible         /project/ansible
COPY backend/controller      /project/controller
COPY buildtools              /project/buildtools
COPY .git                    /project/.git


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
    \
    # workaround for https://github.com/pypa/pip/issues/4180
  && ln -s /project/.git /tmp/.git && ln -s /project/.git /.git \
  && pip2 install --no-cache-dir --upgrade 'setuptools>=26' \
  && pip2 install --no-cache-dir /project/buildtools \
  && pip2 install --no-cache-dir /project/ansible \
  && pip3 install --no-cache-dir /project/controller \
  && /usr/local/bin/decapod-ansible-deploy-config \
  && rm -r /project /tmp/.git /.git \
  && chmod 700 /root/.ssh/ \
  && chmod 600 /root/.ssh/id_rsa \
  && apt-get clean \
  && apt-get purge -y git libssl-dev libffi-dev python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-controller"]
