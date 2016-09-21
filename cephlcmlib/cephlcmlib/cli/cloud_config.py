#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import functools
import sys
import uuid

import six.moves
import yaml


IP_FILENAME = "/tmp/__ip__"
"""Temporary filename to store default IP address."""

UUID_FILENAME = "/tmp/__uuid__"
"""Temporary filename to store machine UUID."""

DEFAULT_USER = "ansible"
"""Default user for Ansible."""

PYTHON_PROG = """
import json,urllib2
d={{"username":{username!r},"host":open({ip_filename!r}).read(),"id":open({uuid_filename!r}).read()}}
r=urllib2.Request({url!r},json.dumps(d))
r.add_header("Content-Type","application/json")
r.add_header("Authorization",{token!r})
print(urllib2.urlopen(r).read())
""".strip()
"""Python program to use instead of Curl."""


def bootcmd(func):
    @functools.wraps(func)
    def decorator(options):
        command = func(options)
        if options.debug:
            return ["sh", "-xc", command]

        return ["sh", "-c", command]

    return decorator


def main():
    options = get_options()

    document = {
        "users": get_users(options),
        "bootcmd": get_bootcmd(options)
    }

    print("#cloud-config")
    print(yaml.dump(document, indent=2, width=9999))


def get_users(options):
    return [
        {
            "name": options.username,
            "groups": ["sudo", options.group or options.username],
            "shell": "/bin/bash",
            "sudo": ["ALL=(ALL) NOPASSWD:ALL"],
            "ssh-authorized-keys": [options.public_key.read().strip()]
        }
    ]


def get_bootcmd(options):
    bootcmd = [
        get_command_header(options),
        get_command_debug(options),
        get_command_uuid(options),
        get_command_ip(options),
        get_command_notify(options),
        get_command_clean(options),
        get_command_footer(options)
    ]
    if not options.debug:
        bootcmd = bootcmd[2:-1]

    return bootcmd


def get_command_header(options):
    return ["echo", "=== START CEPHLCM SERVER DISCOVERY ==="]


def get_command_debug(options):
    return [
        "echo",
        "DISCOVERY DATA: URL={0!r}, TOKEN={1!r}".format(
            options.url, str(options.token))
    ]


@bootcmd
def get_command_uuid(options):
    return (
        "dmidecode | grep UUID | rev | cut -f1 -d' ' | rev | "
        "tr '[[:upper:]]' '[[:lower:]]' {0}".format(
            shell_redirect(options, UUID_FILENAME))
    )


@bootcmd
def get_command_ip(options):
    return (
        "ip route get $(getent ahostsv4 {0!r} | head -n1 | cut -f1 -d' ') | "
        "head -n1 | rev | cut -f2 -d' ' | rev {1}".format(
            get_hostname(options.url), shell_redirect(options, IP_FILENAME)
        )
    )


def get_command_notify(options):
    url = options.url
    if not url.startswith(("http://", "https://")):
        url = "http://{0}".format(url)

    program = PYTHON_PROG.format(
        username=options.username,
        ip_filename=IP_FILENAME,
        uuid_filename=UUID_FILENAME,
        url=url,
        token=str(options.token)
    )
    program = ";".join(program.split("\n"))

    return ["python2", "-c", program]


def get_command_clean(options):
    return ["rm", UUID_FILENAME, IP_FILENAME]


def get_command_footer(options):
    return ["echo", "=== FINISH CEPHLCM SERVER DISCOVERY ==="]


def shell_redirect(options, filename):
    ending = "| tr -d '[[:space:]]' "

    if options.debug:
        ending += "| tee {0}".format(filename)
    else:
        ending += "> {0}".format(filename)

    return ending


def get_hostname(hostname):
    if not hostname.startswith(("http://", "https://")):
        hostname = "http://{0}".format(hostname)

    parsed = six.moves.urllib.parse.urlparse(hostname)
    parsed = parsed.netloc.split(":", 1)[0]

    return parsed


def get_options():
    parser = argparse.ArgumentParser(
        description=(
            "Generate user data configuration for cloud-init on cephlcm "
            "cluster hosts."
        )
    )

    parser.add_argument(
        "url",
        help="URL of CephLCM API."
    )
    parser.add_argument(
        "token",
        help="Server token.",
        type=uuid.UUID
    )
    parser.add_argument(
        "-k", "--public-key",
        help=(
            "Path to the public key file. If nothing is provided, then "
            "stdin will be used as a source."
        ),
        default=sys.stdin,
        nargs="?",
        type=argparse.FileType("r")
    )
    parser.add_argument(
        "-u", "--username",
        help="Username for Ansible to use. Default is {0!r}.".format(
            DEFAULT_USER),
        default=DEFAULT_USER
    )
    parser.add_argument(
        "-g", "--group",
        help="Group of Ansible user to use. Default is given username."
    )
    parser.add_argument(
        "-d", "--debug",
        help="Generate debugable cloud config.",
        action="store_true",
        default=False
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
