# vi: set ft=dockerfile :


FROM nginx:stable-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Base image with frontend for Decapod" version="0.2" vendor="Mirantis"


COPY containerization/files/nginx.conf /etc/nginx/nginx.conf
COPY ssl.key /ssl/ssl.key
COPY ssl.crt /ssl/ssl.crt
COPY ssl-dhparam.pem /ssl/dhparam.pem
COPY ui/build /static
