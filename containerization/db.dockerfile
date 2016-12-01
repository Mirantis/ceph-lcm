# vi: set ft=dockerfile :


FROM mongo:3.2
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with database for Decapod" version="0.2.0" vendor="Mirantis"


COPY containerization/files/mongod.conf /etc/mongod.conf
COPY mongodb.pem /certs/mongodb.pem
COPY mongodb-ca.crt /certs/mongodb-ca.crt
COPY containerization/files/db-moshell.sh /usr/bin/moshell


RUN chmod 0755 /usr/bin/moshell


CMD ["--config", "/etc/mongod.conf"]
