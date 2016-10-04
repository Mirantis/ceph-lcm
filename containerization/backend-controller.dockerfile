# vi: set ft=dockerfile :


FROM cephlcm-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY ansible_ssh_keyfile.pem /root/.ssh/id_rsa


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    libpython2.7 \
    libssl1.0.0 \
    libssl-dev \
    openssh-client \
    python2.7 \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    python-setuptools \
  && pip2 install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_ansible*.whl \
  && pip3 install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_controller*.whl \
  && /usr/local/bin/cephlcm-ansible-deploy-config \
  && rm -r /eggs /constraints.txt \
  && chmod 700 /root/.ssh/ \
  && chmod 600 /root/.ssh/id_rsa \
  && apt-get clean \
  && apt-get purge -y libssl-dev python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["cephlcm-controller"]
