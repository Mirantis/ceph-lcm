# vi: set ft=dockerfile :


FROM decapod-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Controller service for Decapod" version="0.2.0" vendor="Mirantis"


COPY output/eggs /eggs
COPY ansible_ssh_keyfile.pem /root/.ssh/id_rsa


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
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
  && pip2 install --compile --no-cache-dir --disable-pip-version-check /eggs/decapod_ansible*.whl \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/decapod_controller*.whl \
  && /usr/local/bin/decapod-ansible-deploy-config \
  && rm -r /eggs \
  && chmod 700 /root/.ssh/ \
  && chmod 600 /root/.ssh/id_rsa \
  && apt-get clean \
  && apt-get purge -y libssl-dev libffi-dev python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-controller"]
