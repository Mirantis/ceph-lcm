#!/bin/sh

dockerize -wait tcp://database:27017 -timeout 60s decapod-admin "$@"
