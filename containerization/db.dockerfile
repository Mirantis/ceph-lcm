# vi: set ft=dockerfile :


FROM mongo:3.2.10
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/mongod.conf /etc/mongod.conf
COPY mongodb.pem /certs/mongodb.pem


CMD ["--config", "/etc/mongod.conf"]
