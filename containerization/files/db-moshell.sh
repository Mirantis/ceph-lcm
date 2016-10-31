#!/bin/sh

mongo --ssl --sslAllowInvalidHostnames false --sslCAFile /certs/mongodb-ca.crt "$@"
