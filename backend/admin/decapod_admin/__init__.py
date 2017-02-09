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
"""Decapod Admin tools package."""


import asyncio

try:
    import uvloop
except ImportError:
    uvloop = None
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


import decapod_api  # NOQA
from decapod_admin import ceph_version  # NOQA
from decapod_admin import cloud_config  # NOQA
from decapod_admin import db  # NOQA
from decapod_admin import keystone  # NOQA
from decapod_admin import locked_servers  # NOQA
from decapod_admin import migration  # NOQA
from decapod_admin import pdsh  # NOQA
from decapod_admin import restore  # NOQA
from decapod_admin import ssh  # NOQA
