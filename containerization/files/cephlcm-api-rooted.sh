#!/bin/sh
set -eux


cephlcm-api-ensure-indexes
cephlcm-api-inject-root-user
uwsgi /etc/cephlcm-api-uwsgi.ini
