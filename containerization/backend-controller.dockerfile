FROM cephlcm-base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY backend/controller/requirements.txt /controller-requirements.txt
COPY backend/controller/ansible_execution_step_callback/cb_execution.py /cb_execution.py


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    ansible \
    gcc \
    python3-dev \
    python3-pip \
    python-dev \
    python-pip \
    python-setuptools \
  && pip3 install --no-cache-dir --disable-pip-version-check \
    -c /constraints.txt \
    -r /controller-requirements.txt \
    /eggs/cephlcm_controller*.tar.gz \
  && pip2 install --no-cache-dir --disable-pip-version-check -c /constraints.txt pymongo \
  && mkdir -p /usr/share/ansible/plugins/callback \
  && rm -r /eggs /constraints.txt /controller-requirements.txt /cb_execution.py \
  && apt-get clean \
  && apt-get purge -y python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/local/bin/dumb-init", "-c", "cephlcm-controller", "start"]
