# vi: set ft=dockerfile :


FROM python:3.5-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY constraints.txt /constraints.txt
COPY containerization/files/cephlcm-cli.sh /usr/bin/cephlcm-cli
COPY output/eggs /eggs


RUN set -x \
  && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcmlib*.whl \
  && pip3 install --no-cache-dir --disable-pip-version-check /eggs/cephlcm_cli*.whl \
  && touch /etc/cephlcm.sh \
  && chmod 0755 /usr/bin/cephlcm-cli \
  && rm -r /constraints.txt /eggs


ENTRYPOINT ["/bin/sh", "/usr/bin/cephlcm-cli"]
