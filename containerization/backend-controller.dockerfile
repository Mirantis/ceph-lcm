# vi: set ft=dockerfile :


FROM cephlcm-plugins-base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY backend/controller/ansible_execution_step_callback/cb_execution.py /usr/share/ansible/plugins/callback/cb_execution.py
COPY containerization/files/ansible.cfg /etc/ansible/ansible.cfg


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
  && pip3 install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_controller*.whl \
  && pip2 install --no-cache-dir --disable-pip-version-check -c /constraints.txt pymongo \
  && rm -r /eggs /constraints.txt \
  && apt-get clean \
  && apt-get purge -y python-pip python-dev gcc python3-dev python3-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["cephlcm-controller"]
