# vi: set ft=dockerfile :


FROM nginx:stable-alpine
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


COPY containerization/files/nginx.conf /etc/nginx/nginx.conf
COPY ssl.key /ssl/ssl.key
COPY ssl.crt /ssl/ssl.crt
COPY ssl-dhparam.pem /ssl/dhparam.pem
COPY ui/build /static
