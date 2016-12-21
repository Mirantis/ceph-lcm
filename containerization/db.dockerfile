# vi: set ft=dockerfile :


FROM docker-prod-virtual.docker.mirantis.net/mongo:3.2
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Base image with database for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
  && apt-get clean \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


COPY containerization/files/db-moshell.sh /usr/bin/moshell
COPY containerization/files/mongod.conf   /etc/mongod.conf
COPY debian_apt.list                      /etc/apt/sources.list
COPY mongodb-ca.crt                       /certs/mongodb-ca.crt
COPY mongodb.pem                          /certs/mongodb.pem


RUN chmod 0755 /usr/bin/moshell


CMD ["--config", "/etc/mongod.conf"]
