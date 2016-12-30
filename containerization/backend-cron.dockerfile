# vi: set ft=dockerfile :


FROM decapod/controller
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Different cron jobs for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


COPY .git /project/.git


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    cron \
    curl \
    gcc \
    git \
    python-dev \
    python-pip \
    \
    # workaround for https://github.com/pypa/pip/issues/4180
  && ln -s /project/.git /tmp/.git && ln -s /project/.git /.git \
  && cd /project \
  && git reset --hard \
  && scd -v \
  && pip2 install --no-cache-dir /project/backend/monitoring \
  && curl --silent --show-error --fail --location \
    --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" -o - \
    "https://caddyserver.com/download/build?os=linux&arch=amd64&features=" | \
    tar --no-same-owner -C /usr/bin/ -xz caddy \
  && chmod 0755 /usr/bin/caddy \
  && mkdir -p /www \
  && cat /project/containerization/files/crontab | crontab - \
  && mkdir -p /etc/caddy \
  && mv /project/containerization/files/cron-caddyfile /etc/caddy/config \
  && mkfifo /var/log/cron.log \
  && rm -r /project /tmp/.git /.git \
  && apt-get clean \
  && apt-get purge -y git gcc python-dev python-pip curl \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


EXPOSE 8000

CMD ["dockerize", "-wait", "tcp://database:27017", "--", "sh", "-c", "caddy -conf '/etc/caddy/config' & cron && tail -F /var/log/cron.log"]
