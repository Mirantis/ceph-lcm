# vi: set ft=dockerfile :


FROM cephlcm-controller
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>

COPY output/eggs /eggs
COPY constraints.txt /constraints.txt
COPY containerization/files/crontab /cephlcm


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    cron \
    python-dev \
    python-pip \
  && pip install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_monitoring*.whl \
  && cat /cephlcm | crontab - \
  && mkfifo /var/log/cron.log \
  && rm -r /cephlcm /eggs /constraints.txt \
  && apt-get clean \
  && apt-get purge -y gcc python-dev python-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["/usr/bin/dumb-init", "-c", "--"]
CMD ["sh", "-c", "cron && tail -F /var/log/cron.log"]
