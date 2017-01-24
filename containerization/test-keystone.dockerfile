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


FROM krystism/openstack-keystone
MAINTAINER Mirantis Inc.

ARG pip_index_url=
ARG npm_registry_url=
ENV ADMIN_PASSWORD=nomoresecret
STOPSIGNAL SIGINT

COPY containerization/files/test-keystone-bootstrap.sh /etc/bootstrap.sh

RUN set -x \
  && chmod +x /etc/bootstrap.sh
