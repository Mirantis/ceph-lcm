# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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


import configparser
import json
import os.path
import pathlib
import shutil
import subprocess
import tempfile
import textwrap

import click
import pkg_resources
import yaml

from decapod_admin import main
from decapod_api import handlers
from decapod_common import log
from decapod_common import pathutils
from decapod_common import plugins
from decapod_common import process
from decapod_common.models import kv
from decapod_common.models import playbook_configuration
from decapod_common.models import task


LOG = log.getLogger(__name__)
"""Logger."""


@main.cli.command(name="external-execution")
@click.argument(
    "playbook-configuration-id",
    type=click.UUID
)
@click.argument(
    "playbook-configuration-version",
    type=click.INT
)
@click.argument(
    "path",
    required=False,
    type=click.Path(
        dir_okay=False,
        exists=False,
        file_okay=True,
        writable=True
    )
)
@click.pass_context
def external_execution(ctx, playbook_configuration_id,
                       playbook_configuration_version, path):
    """Create bundle for external execution.

    This command creates tarball which has everything required for
    external execution of the plugin. This tarball includes commandline
    for execution with Ansible, the contents of the plugin, generated
    dynamic inventory.

    Please pay attention to following:

    \b
      - This execution won't be added to the decapod and
        will be done without any Decapod interaction
      - You should have installed Ansible 2.3 or newer
      - Please be sure that ceph-ansible is present in role path
        of the ansible.

    http://docs.ansible.com/ansible/intro_configuration.html#roles-path
    https://github.com/ceph/ceph-ansible
    """

    playbook_configuration_id = str(playbook_configuration_id)
    subdir_path = "{0}-{1}".format(
        playbook_configuration_id,
        playbook_configuration_version
    )
    if path is None:
        path = subdir_path
    path = pathlib.Path(path).absolute()

    playbook_config = \
        playbook_configuration.PlaybookConfigurationModel.find_version(
            playbook_configuration_id, playbook_configuration_version)
    if not playbook_config:
        ctx.fail("Cannot find such playbook config")

    plugin = get_plugin(playbook_config.playbook_id)
    working_dir = tempfile.TemporaryDirectory(prefix="exec")
    ctx.call_on_close(working_dir.cleanup)
    working_dir = pathlib.Path(working_dir.name)

    tmpdir = working_dir.joinpath(subdir_path).absolute()
    tmpdir.mkdir()
    tmpdir.joinpath("fetch_directory").mkdir()

    copy_decapod_common_playbooks(tmpdir)
    copy_ceph_ansible(tmpdir)
    copy_private_ssh_key(tmpdir)
    copy_ansible_config(tmpdir)
    copy_plugin_contents(tmpdir, plugin)
    copy_monitor_keyring(tmpdir, playbook_config)
    copy_decapod_data(tmpdir, playbook_config)
    dump_inventory(tmpdir, playbook_config)
    compose_commandline(tmpdir, playbook_config)

    shutil.make_archive(path.as_posix(), "gztar", working_dir.as_posix())
    click.echo(path.with_suffix(".tar.gz").as_posix())


def copy_decapod_common_playbooks(path):
    destpath = path.joinpath("common_playbooks")

    path_to_common_playbooks = pathutils.resource(
        "decapod_common", "playbooks"
    )
    shutil.copytree(path_to_common_playbooks.as_posix(), destpath.as_posix())


def copy_ceph_ansible(path):
    destpath = path.joinpath("ceph-ansible")

    ceph_ansible_path = subprocess.check_output(
        [
            "python2", "-c",
            (
                "import pkg_resources; print "
                "pkg_resources.resource_filename('decapod_ansible', "
                "'ceph-ansible')"
             )
        ]
    )
    ceph_ansible_path = ceph_ansible_path.decode("utf-8").rstrip()

    shutil.copytree(ceph_ansible_path, destpath.as_posix())


def copy_private_ssh_key(path):
    destpath = path.joinpath("ssh-private-key.pem")
    sourcepath = pathutils.HOME.joinpath(".ssh", "id_rsa")

    shutil.copy(sourcepath.as_posix(), destpath.as_posix())
    destpath.chmod(0o400)


def copy_ansible_config(path):
    destpath = path.joinpath("ansible.cfg")
    sourcepath = pathutils.ROOT.joinpath("etc", "ansible", "ansible.cfg")

    shutil.copy2(sourcepath.as_posix(), destpath.as_posix())

    parser = configparser.RawConfigParser()
    with destpath.open() as fp:
        parser.read_file(fp)

    defaults_to_remove = (
        "action_plugins",
        "callback_plugins",
        "connection_plugins",
        "filter_plugins",
        "lookup_plugins",
        "vars_plugins"
    )

    for name in defaults_to_remove:
        try:
            parser.remove_option("defaults", name)
        except Exception:
            pass

    try:
        parser.remove_section("ssh_connection")
    except Exception:
        pass

    parser.set("defaults", "roles_path", "ceph-ansible/roles")
    parser.set("defaults", "private_key_file", "ssh-private-key.pem")
    parser.set("defaults", "action_plugins", "ceph-ansible/plugins/actions")

    with destpath.open("w") as fp:
        parser.write(fp)


def copy_plugin_contents(path, plugin):
    module_name = plugin.module_name.split(".", 1)[0]
    plugin_path = path.joinpath("plugin")
    plugin_path.mkdir()

    for entry in plugin.dist.resource_listdir(module_name):
        if entry == "__pycache__":
            continue

        filename = plugin.dist.get_resource_filename(
            pkg_resources._manager,
            os.path.join(module_name, entry)
        )
        filename = pathlib.Path(filename).absolute()
        destpath = plugin_path.joinpath(filename.name)

        if filename.is_dir():
            shutil.copytree(filename.as_posix(), destpath.as_posix(),
                            symlinks=True)
        else:
            shutil.copy2(filename.as_posix(), destpath.as_posix(),
                         follow_symlinks=False)


def copy_monitor_keyring(path, config):
    secret = kv.KV.find_one("monitor_secret",
                            config.configuration["global_vars"]["fsid"])
    if secret:
        path.joinpath("fetch_directory", "monitor_keyring").write_text(
            secret.value
        )


def copy_decapod_data(path, config):
    destpath = path.joinpath("decapod_data")
    destpath.mkdir()

    destpath.joinpath("playbook-configuration.json").write_text(
        json_dumps(config)
    )
    destpath.joinpath("cluster.json").write_text(json_dumps(config.cluster))

    server_path = destpath.joinpath("servers")
    server_path.mkdir()
    for srv in config.servers:
        server_path.joinpath("{0}.json".format(srv.model_id)).write_text(
            json_dumps(srv)
        )
        server_path.joinpath("{0}.json".format(srv.ip)).symlink_to(
            "{0}.json".format(srv.model_id)
        )

    cluster_servers_path = destpath.joinpath("cluster_servers")
    cluster_servers_path.mkdir()
    for srv in config.cluster.server_list:
        cluster_servers_path.joinpath(
            "{0}.json".format(srv.model_id)).write_text(
            json_dumps(srv)
        )
        cluster_servers_path.joinpath("{0}.json".format(srv.ip)).symlink_to(
            "{0}.json".format(srv.model_id)
        )


def dump_inventory(path, config):
    inventory = config.configuration["inventory"]
    hostvars = inventory.get("_meta", {})
    hostvars = hostvars.get("hostvars", {})

    children = {}
    yaml_inventory = {
        "all": {"children": children},
        "vars": {},
    }
    for groupname, groupstruct in inventory.items():
        if groupname == "_meta":
            continue

        hostsdict = {}
        children[groupname] = {
            "hosts": hostsdict,
            "vars": {}
        }
        if isinstance(groupstruct, dict):
            children[groupname]["vars"] = groupstruct["vars"]
            for hostname in groupstruct["hosts"]:
                hostsdict[hostname] = hostvars.get(hostname, {})
        else:
            for hostname in groupstruct:
                hostsdict[hostname] = hostvars.get(hostname, {})

    path.joinpath("inventory.yaml").write_text(
        yaml.dump(yaml_inventory,
                  default_flow_style=False, explicit_start=True, indent=4)
    )


def compose_commandline(path, playbook_config):
    destpath = path.joinpath("execute.sh")
    faketask = task.PlaybookPluginTask(
        playbook_config.playbook_id, playbook_config._id, None)

    plugin = plugins.get_public_playbook_plugins()[playbook_config.playbook_id]
    plugin = plugin()
    plugin.compose_command(faketask)
    proc = plugin.proc

    proc.env = {}
    proc.options["--inventory-file"] = "inventory.yaml"
    extras = json.loads(proc.options["--extra-vars"])
    extras["decapod_common_playbooks"] = "../common_playbooks"
    extras["fetch_directory"] = "fetch_directory"
    extras = patch_plugin_paths(extras, plugin)
    proc.options["--extra-vars"] = process.jsonify(extras)
    proc.command = "ansible-playbook"
    proc.args = [
        path.joinpath("plugin", plugin.playbook_filename)
        .relative_to(path).as_posix()
    ]

    shell_script = """\
    #!/bin/bash
    set +e
    cd "$(dirname "$0")"

    {0}

    cd - >/dev/null 2>&1
    """.format(proc.printable_commandline)
    shell_script = textwrap.dedent(shell_script)

    destpath.write_text(shell_script)
    destpath.chmod(0o755)


def patch_plugin_paths(extras, plugin):
    if isinstance(extras, dict):
        return {k: patch_plugin_paths(v, plugin) for k, v in extras.items()}
    elif isinstance(extras, list):
        return [patch_plugin_paths(el, plugin) for el in extras]
    elif isinstance(extras, str):
        module_name = plugin.module_name.split(".", 1)[0]
        local_path = pkg_resources.resource_filename(module_name, "")
        return extras.replace(local_path + "/", "")

    return extras


def get_plugin(plugin_id):
    all_plugins = {
        pkg.name: pkg
        for pkg in pkg_resources.iter_entry_points(group=plugins.NS_PLAYBOOKS)
    }
    return all_plugins[plugin_id]


def json_dumps(data):
    return json.dumps(data, cls=handlers.JSONEncoder, sort_keys=True, indent=4)
