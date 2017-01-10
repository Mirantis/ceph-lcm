# vi: set ft=dockerfile :


FROM docker-prod-virtual.docker.mirantis.net/mongo:3.2
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Base image with database for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


COPY containerization/files/db-moshell.sh             /usr/bin/moshell
COPY containerization/files/devconfigs/mongodb-ca.crt /certs/mongodb-ca.crt
COPY containerization/files/devconfigs/mongodb.pem    /certs/mongodb.pem
COPY containerization/files/mongod.conf               /etc/mongod.conf


RUN chmod 0755 /usr/bin/moshell


CMD ["--config", "/etc/mongod.conf"]
