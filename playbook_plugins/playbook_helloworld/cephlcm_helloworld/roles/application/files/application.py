# -*- coding: utf-8 -*-


import json


RESPONSE = json.dumps({"result": "ok"}).encode("utf-8")
RESPONSE += b"\n"
RESPONSE_LENGTH = str(len(RESPONSE))


def app(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "application/json"),
        ("Content-Length", RESPONSE_LENGTH)
    ])
    return iter([RESPONSE])
