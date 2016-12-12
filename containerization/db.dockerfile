# vi: set ft=dockerfile :


FROM mongo:3.2
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with database for Decapod" version="0.2.0" vendor="Mirantis"


COPY containerization/files/db-moshell.sh                    /usr/bin/moshell
COPY containerization/files/mongod.conf                      /etc/mongod.conf
COPY containerization/files/package_managers/debian_apt.list /etc/apt/sources.list
COPY mongodb-ca.crt                                          /certs/mongodb-ca.crt
COPY mongodb.pem                                             /certs/mongodb.pem


RUN chmod 0755 /usr/bin/moshell


CMD ["--config", "/etc/mongod.conf"]
