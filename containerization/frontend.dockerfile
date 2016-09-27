# vi: set ft=dockerfile :


FROM nginx:stable-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/nginx.conf /etc/nginx/nginx.conf
