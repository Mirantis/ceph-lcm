#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import functools

import six
import six.moves
import yaml


IP_FILENAME = "/tmp/__ip__"
"""Temporary filename to store default IP address."""

UUID_FILENAME = "/tmp/__uuid__"
"""Temporary filename to store machine UUID."""

PYTHON_SCRIPT_FILENAME = "/usr/share/server_discovery.py"
"""File where Python script is going to be placed."""

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

PYTHON_PROG = """\
#-*- coding: utf-8 -*-

from __future__ import print_function

import json
import os
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

try:
    os.close(os.open({marker_filename!r}, os.O_CREAT | os.O_EXCL))
except OSError:
    sys.exit(0)

data = {{
    "username": {username!r},
    "host": open({ip_filename!r}).read().strip(),
    "id": open({uuid_filename!r}).read().strip()
}}
data = json.dumps(data).encode("utf-8")

headers = {{
    "Content-Type": "application/json",
    "Authorization": {token!r},
    "User-Agent": "cloud-init server discovery"
}}

request = urllib2.Request({url!r}, data=data, headers=headers)
try:
    urllib2.urlopen(request, timeout={timeout}).read()
except Exception as exc:
    sys.exit(str(exc))

print("Server discovery completed.")
"""
"""Python program to use instead of Curl."""

PACKAGES = (
    "python",
)
"""A list of packages to install with cloud-init."""


class ExplicitDumper(yaml.SafeDumper):
    """A dumper that will never emit aliases."""

    def ignore_aliases(self, data):
        return True


class YAMLLiteral(six.text_type):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(YAMLLiteral, literal_presenter)
ExplicitDumper.add_representer(YAMLLiteral, literal_presenter)


def generate_cloud_config(url, server_discovery_token, public_key, username,
                          timeout=REQUEST_TIMEOUT):
    server_discovery_token = str(server_discovery_token)
    timeout = timeout or REQUEST_TIMEOUT

    if not url.startswith(("http://", "https://")):
        url = "http://{0}".format(url)

    commands = get_commands(url)
    document = {
        "users": get_users(username, public_key),
        "packages": PACKAGES,
        "bootcmd": commands,
        "write_files": get_files(url, server_discovery_token, username,
                                 timeout),
        "runcmd": commands
    }
    cloud_config = yaml.dump(document, Dumper=ExplicitDumper,
                             indent=2, width=9999)
    cloud_config = "#cloud-config\n{0}".format(cloud_config)

    return cloud_config


def get_files(url, server_discovery_token, username, timeout):
    program = PYTHON_PROG.format(
        username=username,
        ip_filename=IP_FILENAME,
        uuid_filename=UUID_FILENAME,
        marker_filename=PYTHON_MARKER_FILENAME,
        url=url,
        token=server_discovery_token,
        timeout=timeout
    )
    return [
        {
            "content": YAMLLiteral(program),
            "path": PYTHON_SCRIPT_FILENAME,
            "permissions": "0440"
        }
    ]


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


def get_commands(url):
    command = [
        get_command_header(),
        get_command_clean(),
        get_command_uuid(),
        get_command_ip(url)
    ]
    command += get_commands_notify()
    command += [
        get_command_clean(),
        get_command_footer()
    ]

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
def get_command_uuid():
    return (
        "dmidecode | grep UUID | rev | cut -f1 -d' ' | rev | "
        "tr '[[:upper:]]' '[[:lower:]]' {0}".format(
            shell_redirect(UUID_FILENAME))
    )


@bootcmd
def get_command_ip(url):
    return (
        "ip route get $(getent ahostsv4 '{0}' | head -n1 | cut -f1 -d' ') | "
        "head -n1 | rev | cut -f2 -d' ' | rev {1}".format(
            get_hostname(url), shell_redirect(IP_FILENAME)
        )
    )


def get_commands_notify():
    return [
        ["python2", PYTHON_SCRIPT_FILENAME],
        ["python3", PYTHON_SCRIPT_FILENAME],
    ]


def get_command_clean():
    return ["rm", "-f", UUID_FILENAME, IP_FILENAME, PYTHON_MARKER_FILENAME]


def get_command_footer():
    return ["echo", "=== FINISH CEPHLCM SERVER DISCOVERY ==="]


def shell_redirect(filename):
    return "| tr -d '[[:space:]]' | tee {0}".format(filename)


def get_hostname(hostname):
    parsed = six.moves.urllib.parse.urlparse(hostname)
    parsed = parsed.netloc.split(":", 1)[0]

    return parsed
