#!/bin/sh

mongo \
    --ssl \
    --sslAllowInvalidHostnames \
    --sslAllowInvalidCertificates \
    --sslCAFile /certs/mongodb-ca.crt \
    "$@"
