# vi: set ft=dockerfile :


FROM nginx:stable-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with frontend for Decapod" version="0.2.0" vendor="Mirantis"


RUN apk add --update ca-certificates openssl \
  && update-ca-certificates \
  && wget https://github.com/jwilder/dockerize/releases/download/v0.3.0/dockerize-linux-amd64-v0.3.0.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.3.0.tar.gz \
  && rm dockerize-linux-amd64-v0.3.0.tar.gz


COPY containerization/files/nginx.conf /etc/nginx/nginx.conf
COPY ssl.key /ssl/ssl.key
COPY ssl.crt /ssl/ssl.crt
COPY ssl-dhparam.pem /ssl/dhparam.pem
COPY ui/build /static


CMD ["dockerize", "-wait", "tcp://api:8000", "--", "nginx", "-g", "daemon off;"]
