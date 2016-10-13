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
    python3-twisted \
  && pip install --no-cache-dir --disable-pip-version-check -c /constraints.txt /eggs/cephlcm_monitoring*.whl \
  && mkdir -p /www \
  && cat /cephlcm | crontab - \
  && mkfifo /var/log/cron.log \
  && rm -r /cephlcm /eggs /constraints.txt \
  && apt-get clean \
  && apt-get purge -y gcc python-dev python-pip \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000

CMD ["sh", "-c", "twistd3 -n web -p 8000 --path /www & cron && tail -F /var/log/cron.log"]
