# vi: set ft=dockerfile :
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM docker-prod-virtual.docker.mirantis.net/mongo:3.4
MAINTAINER Mirantis Inc.


LABEL version="1.2.0" description="Base image with database for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=


HEALTHCHECK --interval=30s --timeout=20s CMD \
  mongo --ssl --sslAllowInvalidCertificates --eval 'db.adminCommand("listDatabases")'


COPY containerization/files/db-backup.sh              /usr/bin/backup
COPY containerization/files/db-moshell.sh             /usr/bin/moshell
COPY containerization/files/db-restore.sh             /usr/bin/restore
COPY containerization/files/devconfigs/mongodb-ca.crt /certs/mongodb-ca.crt
COPY containerization/files/devconfigs/mongodb.pem    /certs/mongodb.pem
COPY containerization/files/mongod.conf               /etc/mongod.conf


RUN chmod 0755 /usr/bin/moshell


ENTRYPOINT ["mongod"]
CMD ["--config", "/etc/mongod.conf"]
