# vi: set ft=dockerfile :


FROM python:3.5-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/decapod-cli.sh /usr/bin/decapod-cli
COPY decapodlib                            /project/lib
COPY decapodcli                            /project/cli


RUN set -x \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check /project/* \
  && chmod 0755 /usr/bin/decapod-cli \
  && rm -r /project


ENTRYPOINT ["/bin/sh", "/usr/bin/decapod-cli"]
