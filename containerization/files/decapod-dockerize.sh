#!/bin/sh

dockerize -wait http://frontend:80/v1/info/ -timeout 60s decapod "$@"
