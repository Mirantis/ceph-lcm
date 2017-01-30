#!/bin/sh

mongodump \
    --ssl \
    --sslAllowInvalidHostnames \
    --sslCAFile /certs/mongodb-ca.crt \
    --archive \
    --gzip \
    2> /dev/null
