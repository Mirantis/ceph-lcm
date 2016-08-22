FROM ubuntu:xenial
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>

RUN set -x \
    && apt update \
    && apt install -y curl tar xz-utils \
    && curl --silent --show-error --fail --location \
       --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" -o - \
       "https://caddyserver.com/download/build?os=linux&arch=amd64&features=cors" \
       | tar --no-same-owner -C /usr/bin/ -xz caddy \
    && chmod 0755 /usr/bin/caddy

EXPOSE 80
ENTRYPOINT ["/usr/bin/caddy"]
CMD ["--conf", "/etc/Caddyfile"]

COPY devstage/Caddyfile /etc/Caddyfile
