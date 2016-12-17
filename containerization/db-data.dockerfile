# vi: set ft=dockerfile :


FROM tianon/true
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL version="0.2.0" description="Base image with database data for Decapod" vendor="Mirantis"
ARG pip_index_url=
ARG npm_registry_url=
