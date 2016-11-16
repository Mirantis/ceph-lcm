# vi: set ft=dockerfile :


FROM python:3.5-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/decapod-cli.sh /usr/bin/decapod-cli
COPY output/eggs /eggs


RUN set -x \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/decapodlib*.whl \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /eggs/decapod_cli*.whl \
  && chmod 0755 /usr/bin/decapod-cli \
  && rm -r /eggs


ENTRYPOINT ["/bin/sh", "/usr/bin/decapod-cli"]
