# vi: set ft=dockerfile :


FROM nginx:stable
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with frontend for Decapod" version="0.2.0" vendor="Mirantis"


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget xz-utils \
  && wget https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz \
  && wget https://nodejs.org/dist/v6.9.2/node-v6.9.2-linux-x64.tar.xz \
  && tar xf node-v6.9.2-linux-x64.tar.xz \
  && mkdir -p /static \
  && apt-get purge -y wget xz-utils \
  && apt-get clean \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


COPY ui                                /ui
COPY containerization/files/nginx.conf /etc/nginx/nginx.conf
COPY ssl.key                           /ssl/ssl.key
COPY ssl.crt                           /ssl/ssl.crt
COPY ssl-dhparam.pem                   /ssl/dhparam.pem


RUN set -x \
  && rm -rf /ui/build /ui/node_modules \
  && PATH=/node-v6.9.2-linux-x64/bin:$PATH sh -c 'cd /ui && npm install && npm run build && npm cache clean' \
  && mv /ui/build/* /static \
  && rm -rf /ui node-v6.9.2-linux*


CMD ["dockerize", "-wait", "tcp://api:8000", "--", "nginx", "-g", "daemon off;"]
