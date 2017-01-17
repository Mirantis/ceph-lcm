# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
