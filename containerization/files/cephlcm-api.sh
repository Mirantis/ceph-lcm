#!/bin/sh


cephlcm-api-ensure-indexes
uwsgi /etc/cephlcm-api-uwsgi.conf
