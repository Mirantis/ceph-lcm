#!/bin/sh

mongodump \
    --ssl \
    --sslAllowInvalidHostnames \
    --sslAllowInvalidCertificates \
    --sslCAFile /certs/mongodb-ca.crt \
    --archive \
    --gzip \
    2> /dev/null
