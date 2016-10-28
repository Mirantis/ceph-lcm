# vi: set ft=dockerfile :


FROM python:3.5-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/cephlcm-cli.sh /usr/bin/cephlcm-cli
COPY output/eggs /eggs


RUN set -x \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/cephlcmlib*.whl \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/cephlcm_cli*.whl \
  && touch /etc/cephlcm.sh \
  && chmod 0755 /usr/bin/cephlcm-cli \
  && rm -r /eggs


ENTRYPOINT ["/bin/sh", "/usr/bin/cephlcm-cli"]
