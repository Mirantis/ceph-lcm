#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


from __future__ import absolute_import
from __future__ import unicode_literals

import six
import six.moves
import yaml


PYTHON_SCRIPT_FILENAME = "/usr/share/server_discovery.py"
"""File where Python script is going to be placed."""

SERVER_DISCOVERY_FILENAME = "/usr/share/server_discovery.sh"
"""File where server discovery script (which should be executed by rc.local)
has to be placed."""

DEFAULT_USER = "ansible"
"""Default user for Ansible."""

REQUEST_TIMEOUT = 5  # seconds
"""How long to wait for response from API."""

SERVER_DISCOVERY_PROG = """\
#!/bin/bash
set -xe -o pipefail

echo "Date $(date) | $(date -u) | $(date '+%s')"

main() {{
    local ip="$(get_local_ip)"
    local hostid="$(get_local_hostid)"

    python {python_script} "$ip" "$hostid"
}}

get_local_ip() {{
    local remote_ipaddr="$(getent ahostsv4 "{url_host}" | head -n 1 | cut -f 1 -d ' ')"

    ip route get "$remote_ipaddr" | head -n 1 | rev | cut -d ' ' -f 2 | rev
}}

get_local_hostid() {{
    dmidecode | grep UUID | rev | cut -d ' ' -f 1 | rev
}}

main
""" # NOQA
"""Script that should be run in /etc/rc.local"""

SERVER_DISCOVERY_LOGFILE = "/var/log/server_discovery.log"
"""Logfile where output of SERVER_DISCOVERY_PROG has to be stored."""

PYTHON_PROG = """\
#-*- coding: utf-8 -*-

from __future__ import print_function

import json
import ssl
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

data = {{
    "username": {username!r},
    "host": sys.argv[1].lower().strip(),
    "id": sys.argv[2].lower().strip()
}}
data = json.dumps(data).encode("utf-8")

headers = {{
    "Content-Type": "application/json",
    "Authorization": {token!r},
    "User-Agent": "cloud-init server discovery"
}}

request = urllib2.Request({url!r}, data=data, headers=headers)
request_kwargs = {{"timeout": {timeout}}}
if sys.version_info >= (2, 7, 9):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    request_kwargs["context"] = ctx

try:
    urllib2.urlopen(request, **request_kwargs).read()
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

    document = {
        "users": get_users(username, public_key),
        "packages": PACKAGES,
        "write_files": get_files(url, server_discovery_token, username,
                                 timeout),
        "runcmd": get_commands(url)
    }
    cloud_config = yaml.dump(document, Dumper=ExplicitDumper,
                             indent=2, width=9999)
    cloud_config = "#cloud-config\n{0}".format(cloud_config)

    return cloud_config


def get_files(url, server_discovery_token, username, timeout):
    python_program = PYTHON_PROG.format(
        username=username,
        url=url,
        token=server_discovery_token,
        timeout=timeout
    )
    rc_local_program = SERVER_DISCOVERY_PROG.format(
        url_host=get_hostname(url),
        python_script=PYTHON_SCRIPT_FILENAME
    )

    return [
        {
            "content": YAMLLiteral(python_program),
            "path": PYTHON_SCRIPT_FILENAME,
            "permissions": "0440"
        },
        {
            "content": YAMLLiteral(rc_local_program),
            "path": SERVER_DISCOVERY_FILENAME,
            "permissions": "0550"
        }
    ]


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
        get_command_update_rc_local(),
        get_command_enable_rc_local(),
        get_command_run_script(),
        get_command_footer()
    ]

    return command


def get_command_header():
    return ["echo", "=== START DECAPOD SERVER DISCOVERY ==="]


def get_command_update_rc_local():
    return [
        "sh", "-xc", (
            r"grep -q '{server_discovery_filename}' /etc/rc.local || "
            r"sed -i 's?^exit 0?{server_discovery_filename} "
            r">> {server_discovery_logfile} 2>\&1\nexit 0?' /etc/rc.local"
        ).format(
            server_discovery_filename=SERVER_DISCOVERY_FILENAME,
            server_discovery_logfile=SERVER_DISCOVERY_LOGFILE
        )
    ]


def get_command_enable_rc_local():
    return [
        "sh", "-xc",
        r"systemctl enable rc-local.service || true"
    ]


def get_command_run_script():
    return [
        "sh", "-xc",
        r"{script} 2>&1 | tee -a {logfile}".format(
            script=SERVER_DISCOVERY_FILENAME,
            logfile=SERVER_DISCOVERY_LOGFILE
        )
    ]


def get_command_footer():
    return ["echo", "=== FINISH DECAPOD SERVER DISCOVERY ==="]


def get_hostname(hostname):
    parsed = six.moves.urllib.parse.urlparse(hostname)
    parsed = parsed.netloc.split(":", 1)[0]

    return parsed
