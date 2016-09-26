# vi: set ft=dockerfile :


FROM cephlcm-plugins-base
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY containerization/files/uwsgi.ini /etc/cephlcm-api-uwsgi.conf


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    python3-pip \
  && pip3 install --no-cache-dir --disable-pip-version-check -c /constraints.txt uwsgi \
  && pip3 install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_api*.whl \
  && apt-get clean \
  && apt-get purge -y python3-dev python3-pip gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["uwsgi", "/etc/cephlcm-api-uwsgi.conf"]
