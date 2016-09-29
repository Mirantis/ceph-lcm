#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import functools
import gzip
import io

import six
import six.moves
import yaml


IP_FILENAME = "/tmp/__ip__"
"""Temporary filename to store default IP address."""

UUID_FILENAME = "/tmp/__uuid__"
"""Temporary filename to store machine UUID."""

PYTHON_MARKER_FILENAME = "/tmp/__server_discovery__"
"""Marker filename for Pythons.

Basically, we do not know if python2 or python3 were installed therefore
we have to try both. To avoid 2 requests for server, we are going to
use marker file. If one python succeed to run, then such file has to be
created. It means that next python won't continue to work.
"""

DEFAULT_USER = "ansible"
"""Default user for Ansible."""

REQUEST_TIMEOUT = 5  # seconds
"""How long to wait for response from API."""

PYTHON_PROG = """
from __future__ import print_function

import json
import os.path
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

if os.path.exists({marker_filename!r}):
    sys.exit(0)

open({marker_filename!r}, "w").close()

data = {{
    "username": {username!r},
    "host": open({ip_filename!r}).read().strip(),
    "id": open({uuid_filename!r}).read().strip()
}}

request = urllib2.Request({url!r}, json.dumps(data).encode("utf-8"))
request.add_header("Content-Type", "application/json")
request.add_header("Authorization", {token!r})
request.add_header("User-Agent", "cloud-init server discovery")

urllib2.urlopen(request, timeout={timeout}).read()
print("Server discovery completed.")
""".strip()
"""Python program to use instead of Curl."""


def generate_cloud_config(url, server_discovery_token, public_key, username,
                          timeout=REQUEST_TIMEOUT, debug=False,
                          to_base64=False):
    server_discovery_token = str(server_discovery_token)
    timeout = timeout or REQUEST_TIMEOUT

    if not url.startswith(("http://", "https://")):
        url = "http://{0}".format(url)

    document = {
        "users": get_users(username, public_key),
        "bootcmd": get_bootcmd(url, server_discovery_token, username, timeout,
                               debug)
    }
    cloud_config = yaml.safe_dump(document, indent=2, width=9999)
    cloud_config = "#cloud-config\n{0}".format(cloud_config)
    cloud_config = cloud_config.rstrip()

    if to_base64:
        if not isinstance(cloud_config, six.binary_type):
            cloud_config = cloud_config.encode("utf-8")
        cloud_config = base64.urlsafe_b64encode(cloud_config)

    return cloud_config


def bootcmd(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        return ["sh", "-xc", func(*args, **kwargs)]

    return decorator


def get_users(username, public_key):
    return [
        {
            "name": username,
            "groups": ["sudo"],
            "shell": "/bin/bash",
            "sudo": ["ALL=(ALL) NOPASSWD:ALL"],
            "ssh-authorized-keys": [public_key]
        }
    ]


def get_bootcmd(url, server_discovery_token, username, timeout, debug):
    command = [
        get_command_header(),
        get_command_debug(url, server_discovery_token),
        get_command_clean(),
        get_command_uuid(debug),
        get_command_ip(url, debug)
    ]
    command += get_commands_notify(url, server_discovery_token, username,
                                   timeout)
    command += [
        get_command_clean(),
        get_command_footer()
    ]
    if not debug:
        command = command[2:-1]

    return command


def get_command_header():
    return ["echo", "=== START CEPHLCM SERVER DISCOVERY ==="]


def get_command_debug(url, server_discovery_token):
    return [
        "echo",
        "DISCOVERY DATA: URL={0!r}, TOKEN={1!r}".format(
            url, server_discovery_token)
    ]


@bootcmd
def get_command_uuid(debug):
    return (
        "dmidecode | grep UUID | rev | cut -f1 -d' ' | rev | "
        "tr '[[:upper:]]' '[[:lower:]]' {0}".format(
            shell_redirect(UUID_FILENAME, debug))
    )


@bootcmd
def get_command_ip(url, debug):
    return (
        "ip route get $(getent ahostsv4 {0!r} | head -n1 | cut -f1 -d' ') | "
        "head -n1 | rev | cut -f2 -d' ' | rev {1}".format(
            get_hostname(url), shell_redirect(IP_FILENAME, debug)
        )
    )


def get_commands_notify(url, server_discovery_token, username, timeout):
    program = PYTHON_PROG.format(
        username=username,
        ip_filename=IP_FILENAME,
        uuid_filename=UUID_FILENAME,
        marker_filename=PYTHON_MARKER_FILENAME,
        url=url,
        token=server_discovery_token,
        timeout=timeout
    )
    program = gzip_text(program)
    program = base64.b64encode(program)
    program = program.decode("utf-8")

    return [
        ["sh", "-xc",
         "echo {0!r} | base64 -d | gzip -d | python2 -".format(program)],
        ["sh", "-xc",
         "echo {0!r} | base64 -d | gzip -d | python3 -".format(program)],
    ]


def get_command_clean():
    return ["rm", "-f", UUID_FILENAME, IP_FILENAME, PYTHON_MARKER_FILENAME]


def get_command_footer():
    return ["echo", "=== FINISH CEPHLCM SERVER DISCOVERY ==="]


def shell_redirect(filename, debug):
    ending = "| tr -d '[[:space:]]' "

    if debug:
        ending += "| tee {0}".format(filename)
    else:
        ending += "> {0}".format(filename)

    return ending


def get_hostname(hostname):
    parsed = six.moves.urllib.parse.urlparse(hostname)
    parsed = parsed.netloc.split(":", 1)[0]

    return parsed


def gzip_text(text):
    text = text.encode("utf-8")

    if hasattr(gzip, "compress"):  # python 3.2+
        return gzip.compress(text, compresslevel=9)

    fileobj = io.BytesIO()
    with gzip.GzipFile(mode="wb", fileobj=fileobj, compresslevel=9) as gzfp:
        gzfp.write(text)

    return fileobj.getvalue()
