#!/bin/sh

mongorestore \
    --ssl \
    --sslAllowInvalidHostnames \
    --sslAllowInvalidCertificates \
    --sslCAFile /certs/mongodb-ca.crt \
    --archive \
    --drop \
    --gzip
