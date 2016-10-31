# vi: set ft=dockerfile :


FROM python:3.5-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/shrimp-cli.sh /usr/bin/shrimp-cli
COPY output/eggs /eggs


RUN set -x \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/shrimplib*.whl \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/shrimp_cli*.whl \
  && touch /etc/cephlcm.sh \
  && chmod 0755 /usr/bin/shrimp-cli \
  && rm -r /eggs


ENTRYPOINT ["/bin/sh", "/usr/bin/shrimp-cli"]
