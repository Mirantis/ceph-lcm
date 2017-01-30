#!/bin/sh

mongorestore \
    --ssl \
    --sslAllowInvalidHostnames \
    --sslCAFile /certs/mongodb-ca.crt \
    --archive \
    --drop \
    --gzip
