# vi: set ft=dockerfile :


FROM cephlcm-controller
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/crontab /cephlcm


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    cron \
  && cat /cephlcm | crontab - \
  && mkfifo /var/log/docker-stdout.log \
  && rm /cephlcm \
  && apt-get clean \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


CMD ["sh", "-c", "cron && tail -F /var/log/docker-stdout.log"]
