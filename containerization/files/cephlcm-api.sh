#!/bin/sh
set -eux


cephlcm-api-ensure-indexes
uwsgi /etc/cephlcm-api-uwsgi.ini
