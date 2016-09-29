#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import functools

import six
import six.moves
import yaml


IP_FILENAME = "/tmp/__ip__"
"""Temporary filename to store default IP address."""

UUID_FILENAME = "/tmp/__uuid__"
"""Temporary filename to store machine UUID."""

DEFAULT_USER = "ansible"
"""Default user for Ansible."""

REQUEST_TIMEOUT = 5  # seconds
"""How long to wait for response from API."""

PYTHON_PROG = """
import json,urllib2
d={{"username":{username!r},"host":open({ip_filename!r}).read(),"id":open({uuid_filename!r}).read()}}
r=urllib2.Request({url!r},json.dumps(d))
r.add_header("Content-Type","application/json")
r.add_header("Authorization",{token!r})
print(urllib2.urlopen(r,timeout={timeout}).read())
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
    bootcmd = [
        get_command_header(),
        get_command_debug(url, server_discovery_token),
        get_command_uuid(debug),
        get_command_ip(url, debug),
        get_command_notify(url, server_discovery_token, username, timeout),
        get_command_clean(),
        get_command_footer()
    ]
    if not debug:
        bootcmd = bootcmd[2:-1]

    return bootcmd


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


def get_command_notify(url, server_discovery_token, username, timeout):
    program = PYTHON_PROG.format(
        username=username,
        ip_filename=IP_FILENAME,
        uuid_filename=UUID_FILENAME,
        url=url,
        token=server_discovery_token,
        timeout=timeout
    )
    program = ";".join(program.split("\n"))

    return ["python2", "-c", program]


def get_command_clean():
    return ["rm", UUID_FILENAME, IP_FILENAME]


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
