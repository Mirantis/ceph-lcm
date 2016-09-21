#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import json
import shlex
import sys

import yaml


IP_FILENAME = "/tmp/__ip__"
"""Temporary filename to store default IP address."""

UUID_FILENAME = "/tmp/__uuid__"
"""Temporary filename to store machine UUID."""


def main():
    options = get_options()
    document = {
        "users": get_users(options),
        "packages": get_packages(options),
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


def get_packages(options):
    return [
        "dmidecode",
        "iproute2",
        "curl"
    ]


def get_bootcmd(options):
    return [
        get_command_uuid(options),
        get_command_ip(options),
        get_command_all(options),
        get_command_clean(options)
    ]


def get_command_uuid(options):
    return [
        "sh", "-c",
        "dmidecode | grep UUID | rev | cut -f1 -d' ' | rev | "
        "tr -d '[[:space:]]' | tr '[[:upper:]]' '[[:lower:]]' > {0}".format(
            UUID_FILENAME)
    ]


def get_command_ip(options):
    return [
        "sh", "-c",
        "ip r g 8.8.8.8 | head -n1 | rev | cut -f2 -d' ' | rev | "
        "tr -d '[[:space:]]' > {0}".format(IP_FILENAME)
    ]


def get_command_all(options):
    return ["sh", "-cx", get_curl_command(options)]


def get_command_clean(options):
    return ["rm", UUID_FILENAME, IP_FILENAME]


def get_curl_command(options):
    request = get_request_data(options)
    request = shlex.quote(request)

    command = ["curl"]
    command.append("--silent")
    command.append("--location")
    command.extend(["--request", "POST"])
    command.extend(["--header", "'Authorization: {0}'".format(options.token)])
    command.extend(["--header", "'Content-Type: application/json'"])
    command.extend(["--data", request])
    command.append(options.url)

    return " ".join(command)


def get_request_data(options):
    data = {
        "id": "$(cat {0})".format(UUID_FILENAME),
        "username": options.username,
        "host": "$(cat {0})".format(IP_FILENAME)
    }
    data = json.dumps(data, separators=(",", ":"))

    return data


def get_options():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "url",
        help="URL of CephLCM API."
    )
    parser.add_argument(
        "token",
        help="Server token."
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
        help="Username for Ansible to use.",
        default="ansible"
    )
    parser.add_argument(
        "-g", "--group",
        help="Group of Ansible user to use."
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
