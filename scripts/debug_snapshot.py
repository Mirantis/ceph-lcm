#!/usr/bin/env python
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
"""This module containers script to perform backup of the Decapod."""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import atexit
import contextlib
import functools
import multiprocessing
import multiprocessing.pool
import os
import os.path
import shutil
import subprocess
import sys
import syslog
import tempfile
import time


SYSLOG_IDENT = "decapod-debug-snapshot"
"""Identity of tool in syslog."""

syslog.openlog(str(SYSLOG_IDENT))


def async(filename=None):
    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(snapshot_dir, *args, **kwargs):
            output = None
            if filename:
                output_filename = os.path.join(snapshot_dir, filename)
                output = open(output_filename, "wb")

            command = None
            try:
                with open(os.devnull, "wb") as wdevnull:
                    with open(os.devnull, "rb") as rdevnull:
                        command = func(snapshot_dir, *args, **kwargs)
                        syslog.syslog(syslog.LOG_INFO,
                                      "Execute command {0}".format(command))
                        subprocess.check_call(
                            command,
                            stdout=output,
                            stdin=rdevnull,
                            stderr=wdevnull
                        )
            except Exception as exc:
                syslog.syslog(syslog.LOG_WARNING, str(exc))
                if output:
                    output.close()
                    os.remove(output.name)
                    output = None
            finally:
                if output:
                    output.close()

        return inner_decorator
    return outer_decorator


@contextlib.contextmanager
def closing_pool(pool):
    try:
        with contextlib.closing(pool) as pll:
            yield pll
    except Exception as exc:
        syslog.syslog(syslog.LOG_WARNING,
                      "Terminate pool due to {0}".format(exc))
        pool.terminate()
        raise
    finally:
        pool.join()


def main(pool):
    options = get_options()
    options.compose_file.close()
    syslog.syslog(syslog.LOG_INFO, "Options are {0}".format(options))

    compose_cmd = get_compose_cmd(options)
    container_ids = get_container_id_mapping(pool, compose_cmd)
    syslog.syslog(syslog.LOG_INFO, "Container ID mapping {0}".format(
        container_ids))

    tmp_dir = tempfile.mkdtemp()
    atexit.register(lambda: shutil.rmtree(tmp_dir))
    syslog.syslog(syslog.LOG_INFO, "Temporary directory: {0}".format(tmp_dir))

    snapshot_dir = os.path.join(tmp_dir, "snapshot")
    for name in container_ids:
        os.makedirs(os.path.join(snapshot_dir, name))

    with closing_pool(pool):
        process_main_files(pool, snapshot_dir, compose_cmd, container_ids)

        for name, container_id in container_ids.items():
            process_service_files(pool, name, container_id, snapshot_dir,
                                  compose_cmd)

    syslog.syslog(syslog.LOG_INFO, "Information was collected.")
    make_archive(tmp_dir, options.snapshot_path)
    syslog.syslog(syslog.LOG_INFO, "Data is collected")


def get_options():
    parser = argparse.ArgumentParser(
        description="Create debug snapshot for Decapod.",
        epilog="Please find all logs in syslog by ident '{0}'.".format(
            SYSLOG_IDENT),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-f", "--compose-file",
        type=argparse.FileType(),
        default=get_compose_file_path(),
        help="path to docker-compose.yml file."
    )
    parser.add_argument(
        "-p", "--project-name",
        default=get_project_name(),
        help="the name of the project."
    )
    parser.add_argument(
        "snapshot_path",
        help="Path where to store snapshot (do not append extension, we will"
             " do it for you)."
    )

    return parser.parse_args()


def get_compose_file_path():
    path = os.getenv("COMPOSE_FILE", os.path.join(
        os.getcwd(), "docker-compose.yml"))
    path = os.path.abspath(path)

    return path


def get_project_name():
    return os.getenv("COMPOSE_PROJECT_NAME", os.path.basename(os.getcwd()))


def process_main_files(pool, snapshot_dir, compose_cmd, container_ids):
    pool.apply_async(collect_backup, [snapshot_dir, compose_cmd])
    pool.apply_async(collect_docker_info, [snapshot_dir])
    pool.apply_async(collect_docker_version, [snapshot_dir])
    pool.apply_async(
        collect_docker_compose_config, [snapshot_dir, compose_cmd])
    pool.apply_async(collect_all_logs, [snapshot_dir, compose_cmd])
    pool.apply_async(collect_monitoring_results,
                     [snapshot_dir, container_ids["admin"]])


def process_service_files(pool, name, container_id, snapshot_dir, compose_cmd):
    service_snapshot_dir = os.path.join(snapshot_dir, name)
    pool.apply_async(collect_service_log,
                     [service_snapshot_dir, name, compose_cmd])
    pool.apply_async(collect_service_date,
                     [service_snapshot_dir, name, compose_cmd])
    pool.apply_async(collect_service_unix_timestamp,
                     [service_snapshot_dir, name, compose_cmd])
    pool.apply_async(collect_service_packages_os,
                     [service_snapshot_dir, name, compose_cmd])
    pool.apply_async(collect_service_ps,
                     [service_snapshot_dir, name, compose_cmd])
    pool.apply_async(collect_service_docker_inspect,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_docker_stats,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_config,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_git_release,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_decapod_release,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_packages_npm,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_packages_python2,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_packages_python3,
                     [service_snapshot_dir, name, container_id])
    pool.apply_async(collect_service_private_key_sha1sum,
                     [service_snapshot_dir, name, compose_cmd])


def make_archive(collected_dir, result_path):
    formats = {name for name, description in shutil.get_archive_formats()}
    for fmt in "xztar", "bztar", "gztar":
        if fmt in formats:
            archive_format = fmt
            break
    else:
        archive_format = "tar"

    shutil.make_archive(result_path, archive_format, collected_dir, "snapshot")


def get_compose_cmd(options):
    return [
        "docker-compose",
        "--project-name", options.project_name,
        "--file", options.compose_file.name
    ]


def get_container_id_mapping(pool, compose_cmd):
    service_names = subprocess.check_output(
        compose_cmd + ["config", "--services"]
    )
    service_names = service_names.strip().decode("utf-8").split("\n")
    id_mapping = {
        name: pool.apply_async(pool_container_id, (name, compose_cmd))
        for name in service_names
    }

    while not all(future.ready() for future in id_mapping.values()):
        time.sleep(0.1)
    for name, future in list(id_mapping.items()):
        if not future.successful():
            raise RuntimeError("Cannot get ID of service {0}".format(name))
        id_mapping[name] = future.get()

    return id_mapping


def pool_container_id(name, compose_cmd):
    container_id = subprocess.check_output(compose_cmd + ["ps", "-q", name])
    container_id = container_id.strip().decode("utf-8")

    return container_id


@async("db-backup")
def collect_backup(_, compose_cmd):
    return compose_exec(compose_cmd, "admin", "decapod-admin", "db", "backup")


@async("docker-info")
def collect_docker_info(_):
    return ["docker", "info"]


@async("docker-version")
def collect_docker_version(_):
    return ["docker", "version"]


@async("docker-compose.yml")
def collect_docker_compose_config(_, compose_cmd):
    return compose_cmd + ["config"]


@async("all.log")
def collect_all_logs(_, compose_cmd):
    return docker_logs(compose_cmd)


@async()
def collect_monitoring_results(snapshot_dir, container_id):
    return docker_cp(
        container_id, "/www/monitoring",
        os.path.join(snapshot_dir, "ceph-monitoring"))


@async("log")
def collect_service_log(_, service_name, compose_cmd):
    return docker_logs(compose_cmd, service_name)


@async("date")
def collect_service_date(_, service_name, compose_cmd):
    return compose_exec(compose_cmd, service_name, "date")


@async("timestamp")
def collect_service_unix_timestamp(_, service_name, compose_cmd):
    return compose_exec(compose_cmd, service_name, "date", "+%s")


@async("packages-os")
def collect_service_packages_os(_, service_name, compose_cmd):
    return compose_exec(compose_cmd, service_name, "dpkg", "-l")


@async("ps")
def collect_service_ps(_, service_name, compose_cmd):
    return compose_exec(compose_cmd, service_name, "ps", "auxfww")


@async("docker-inspect")
def collect_service_docker_inspect(_, service_name, container_id):
    return ["docker", "inspect", "--type", "container", container_id]


@async("docker-stats")
def collect_service_docker_stats(_, service_name, container_id):
    return ["docker", "stats", "--no-stream", container_id]


@async("private_key_sha1sum")
def collect_service_private_key_sha1sum(_, service_name, compose_cmd):
    return compose_exec(compose_cmd, service_name,
                        "sha1sum", "/root/.ssh/id_rsa")


@async()
def collect_service_config(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/etc/decapod/config.yaml", snapshot_dir)


@async()
def collect_service_git_release(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/etc/git-release", snapshot_dir)


@async()
def collect_service_decapod_release(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/etc/decapod-release", snapshot_dir)


@async()
def collect_service_packages_npm(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/packages-npm", snapshot_dir)


@async()
def collect_service_packages_python2(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/packages-python2", snapshot_dir)


@async()
def collect_service_packages_python3(snapshot_dir, service_name, container_id):
    return docker_cp(container_id, "/packages-python3", snapshot_dir)


def docker_cp(container_id, remote_path, local_path):
    return [
        "docker", "cp",
        "{0}:{1}".format(container_id, remote_path),
        local_path
    ]


def compose_exec(compose_cmd, service_name, *command):
    return compose_cmd + ["exec", "-T", service_name] + list(command)


def docker_logs(compose_cmd, service_name=None):
    command = compose_cmd + ["logs", "--no-color", "-t"]
    if service_name:
        command.append(service_name)

    return command


if __name__ == "__main__":
    sys.exit(main(multiprocessing.pool.Pool()))
