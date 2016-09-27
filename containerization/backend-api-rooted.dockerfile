# vi: set ft=dockerfile :


FROM cephlcm-api
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/cephlcm-api-inject-root-user.py /usr/local/bin/cephlcm-api-inject-root-user
COPY containerization/files/cephlcm-api-rooted.sh /usr/local/bin/cephlcm-api


RUN set -x \
  && chmod 0755 /usr/local/bin/cephlcm-api-inject-root-user /usr/local/bin/cephlcm-api
