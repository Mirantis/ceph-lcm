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
"""Various utils for Decapod Admin CLI."""


import asyncio
import configparser
import functools
import http.client
import json
import logging
import os
import pathlib
import random
import subprocess
import sys
import time
import uuid

import asyncssh
import click

from decapod_common import log


IP_LENGTH = len("255.255.255.255")
"""Length of IP address in string."""

UUID_LENGTH = len(str(uuid.uuid4()))
"""Length of UUID in string."""

LOG = log.getLogger(__name__)
"""Logger."""


class SSHClientSession(asyncssh.SSHClientSession):

    def __init__(self, srv):
        super().__init__()

        self.obuffer = ""
        self.ebuffer = ""
        self.prefix = make_ssh_output_prefix(srv)

    def data_received(self, data, datatype):
        if datatype == asyncssh.EXTENDED_DATA_STDERR:
            self.ebuffer += data
            self.ebuffer = self.doprint(self.ebuffer, stderr=True)
        else:
            self.obuffer += data
            self.obuffer = self.doprint(self.obuffer, stderr=False)

        return super().data_received(data, datatype)

    def doprint(self, buf, *, flush=False, stderr=False):
        if not buf:
            return buf

        stream = sys.stderr if stderr else sys.stdout

        if flush:
            print(self.data(buf), file=stream)
            return ""

        buf = buf.split("\n")
        for chunk in buf[:-1]:
            print(self.data(chunk), file=stream)

        return buf[-1] if buf else ""

    def data(self, text):
        return self.prefix + text

    def connection_lost(self, exc):
        self.doprint(self.obuffer, stderr=False, flush=True)
        self.doprint(self.ebuffer, stderr=True, flush=True)

        if exc:
            LOG.warning("SSH connection %s has been dropped: %s", self, exc)

        super().connection_lost(exc)


def configure_logging(debug):
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.propagate = True

    if debug:
        http.client.HTTPConnection.debuglevel = 1
        requests_log.setLevel(logging.DEBUG)
    else:
        http.client.HTTPConnection.debuglevel = 0
        requests_log.setLevel(logging.CRITICAL)


def json_loads(data):
    return json.loads(data)


def json_dumps(data):
    return json.dumps(data, indent=4, sort_keys=True)


def sleep_with_jitter(work_for=None, max_jitter=20):
    current_time = start_time = time.monotonic()
    jitter = 0

    while work_for < 0 or (current_time < start_time + work_for):
        # https://www.awsarchitectureblog.com/2015/03/backoff.html
        jitter = min(max_jitter, jitter + 1)
        yield current_time - start_time
        time.sleep(random.uniform(0, jitter))
        current_time = time.monotonic()

    yield current_time - start_time


def command(command_class, *, name=None):
    def decorator(func):
        nonlocal name

        if name is None:
            name = func.__name__.replace("_", "-")
        func = command_class.command(name=name)(func)

        return func

    return decorator


def spawn(command, *,
          stdin=subprocess.DEVNULL, stdout=None, stderr=subprocess.DEVNULL,
          shell=False, timeout=None):
    return subprocess.run(
        command,
        stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, timeout=timeout
    )


@functools.lru_cache()
def get_private_key_path():
    default_path = os.getenv("ANSIBLE_CONFIG", "/etc/ansible/ansible.cfg")
    default_path = pathlib.Path(default_path)
    parser = configparser.RawConfigParser()
    parser.read(str(default_path))

    path = parser.get(
        "defaults", "private_key_file",
        fallback=str(pathlib.Path.home().joinpath(".ssh", "id_rsa")))
    path = pathlib.Path(str(path))

    return path


def make_ssh_output_prefix(srv):
    return "{0} | {1}: ".format(
        srv.model_id.ljust(UUID_LENGTH),
        srv.ip.ljust(IP_LENGTH)
    )


def ssh_command(func):
    func = click.option(
        "-i", "--identity-file",
        type=click.File(lazy=False),
        default=str(get_private_key_path()),
        help="Path to the private key file",
        show_default=True
    )(func)
    func = click.option(
        "-b", "--batch-size",
        type=int,
        default=20,
        help="By default, command won't connect to all servers "
             "simultaneously, it is trying to process servers in batches. "
             "Negative number or 0 means connect to all hosts",
        show_default=True,
    )(func)

    @functools.wraps(func)
    @click.pass_context
    def decorator(ctx, identity_file, batch_size, *args, **kwargs):
        private_key = asyncssh.import_private_key(identity_file.read())
        batch_size = batch_size if batch_size > 0 else None
        identity_file.close()

        ctx.obj["private_key"] = private_key
        ctx.obj["batch_size"] = batch_size
        ctx.obj["event_loop"] = asyncio.get_event_loop()

        return func(*args, **kwargs)

    return decorator


def async_batch_executor(func):
    @functools.wraps(func)
    async def decorator(ctx, *args, **kwargs):
        servers = ctx.obj["servers"]
        batch_size = ctx.obj["batch_size"]
        if batch_size is None:
            batch_size = len(servers)

        while servers:
            current_server_batch = servers[:batch_size]
            servers = servers[batch_size:]
            if not current_server_batch:
                continue

            tasks = [
                func(ctx, srv, *args, **kwargs) for srv in current_server_batch
            ]
            await asyncio.wait(tasks)

    return decorator


def asyncssh_connector(func):
    @functools.wraps(func)
    async def decorator(ctx, srv, *args, **kwargs):
        connection = asyncssh.connect(
            srv.ip,
            known_hosts=None,
            username=srv.username,
            client_keys=[ctx.obj["private_key"]]
        )

        async with connection as open_connection:
            await func(ctx, srv, open_connection, *args, **kwargs)

    return decorator
