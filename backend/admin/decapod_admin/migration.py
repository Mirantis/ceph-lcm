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
"""Migration related CLI commands."""


import hashlib
import os
import pathlib
import subprocess
import time

import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common import pathutils
from decapod_common.models import lock
from decapod_common.models import migration_script


LOG = log.getLogger(__name__)
"""Logger."""

MIGRATION_SHOW_TEMPLATE = """
Name:           {name}
Result:         {result}
Executed at:    {time}
SHA1 of script: {script_hash}

-- Stdout:
{stdout}
-- Stderr:
{stderr}
""".strip()
"""Template to display for migration.show"""

DIRECTORY = pathutils.resource("decapod_admin", "migration_scripts")
"""Directory where migration scripts are placed."""


@main.cli_group
def migration():
    """Migrations for database."""


@utils.command(migration)
@click.argument(
    "query",
    type=click.Choice(["all", "applied", "not-applied"]),
    default="all"
)
def list(query):
    """List migrations.

    Available query filters are:

    \b
        - all (default) - list all migrations;
        - applied       - list only applied migrations;
        - not-applied   - list only not applied migrations.
    """
    for_listing = {}

    for item in get_migration_scripts(DIRECTORY):
        for_listing[item.name] = False
    for item in migration_script.MigrationScript.find():
        for_listing[item._id] = True

    for name, applied in sorted(for_listing.items()):
        if query == "all":
            applied = "[applied]" if applied else "[not-applied]"
            applied = applied.ljust(len("[not-applied]"), " ")
            click.echo("{0} {1}".format(applied, name))
        elif query == "not_applied":
            if not applied:
                click.echo(name)
        elif applied:
            click.echo(name)


@utils.command(migration)
@click.argument(
    "migration-name",
    nargs=-1
)
@click.option(
    "--reapply", "-r",
    is_flag=True,
    help="Reapply migrations even if them were applied."
)
@click.option(
    "--fake", "-f",
    is_flag=True,
    help="Do not actual run migration, just mark it as applied."
)
@lock.synchronized("applying_migrations", timeout=60)
def apply(reapply, fake, migration_name):
    """Apply migration script.

    If no parameters are given, then run all not applied migration
    scripts if correct order.
    """
    migrations = get_migrations_to_apply(reapply, fake, migration_name)
    if not migrations:
        LOG.info("No migration are required to be applied.")
        return

    for migration in migrations:
        LOG.info("Run migration %s", migration.name)

        try:
            migration.run()
        except Exception:
            ok = False
        else:
            ok = True

        apply_migration(migration, ok=ok)


@utils.command(migration)
@click.argument("migration_name")
def show(migration_name):
    """Show details on applied migration."""
    all_migrations = migration_script.MigrationScript.find()
    all_migrations = {item._id: item for item in all_migrations}

    if migration_name not in all_migrations:
        raise Exception("Cannot find such migration.")

    migration = all_migrations[migration_name]
    message = MIGRATION_SHOW_TEMPLATE.format(
        name=migration._id,
        time=time.ctime(migration.time_executed),
        result=migration.state.name,
        script_hash=migration.script_hash,
        stdout=migration.stdout,
        stderr=migration.stderr
    )

    click.echo(message)


class MigrationScript:

    def __init__(self, path):
        self.path = path
        self.process = None
        self.stdout = ""
        self.stderr = ""

    @property
    def name(self):
        return self.path.name

    @property
    def script_hash(self):
        hasher = hashlib.sha1()

        with self.path.open("rb") as filefp:
            while True:
                data = filefp.read(1024)
                hasher.update(data)
                if not data:
                    break

        return hasher.hexdigest()

    @property
    def finished(self):
        return bool(self.process and self.process.returncode is not None)

    def run(self):
        if self.finished:
            return

        self.process = subprocess.Popen(
            [str(self.path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        LOG.info("Run %s. Pid %d", self.path, self.process.pid)
        self.process.wait()
        logmethod = LOG.info if self.process.returncode == os.EX_OK \
            else LOG.warning
        logmethod("%s has been finished. Exit code %s",
                  self.path, self.process.returncode)

        self.stdout = self.process.stdout.read().decode("utf-8")
        self.stderr = self.process.stderr.read().decode("utf-8")

        if self.process.returncode != os.EX_OK:
            raise RuntimeError(
                "Program {0} has been finished with exit code {1}",
                self.path, self.process.returncode)


def get_migration_scripts(directory):
    return sorted(
        (MigrationScript(name) for name in pathlib.Path(directory).iterdir()
         if name.is_file() and os.access(str(name), os.R_OK | os.X_OK)),
        key=lambda item: item.name
    )


def get_migrations_to_apply(reapply, fake, migration_names):
    avaialble_migrations = get_migration_scripts(DIRECTORY)
    db_migrations = migration_script.MigrationScript.find()
    db_migrations = {item._id for item in db_migrations}

    if not migration_names:
        return get_migrations_to_apply_default(
            reapply, fake, avaialble_migrations, db_migrations)

    migrations_to_apply = get_migrations_list(
        migration_names, avaialble_migrations)

    if reapply:
        return migrations_to_apply

    if fake:
        for migr in migrations_to_apply:
            apply_migration(migr, ok=True)
        return []

    return [migr for migr in migrations_to_apply
            if migr.name not in db_migrations]


def get_migrations_to_apply_default(
        reapply, fake, available_migrations, db_migrations):
    if reapply:
        return available_migrations

    if fake:
        for migr in available_migrations:
            apply_migration(migr, ok=True)
        return []

    return [item for item in available_migrations
            if item.name not in db_migrations]


def get_migrations_list(cli_list, available_migrations):
    cli_list = set(cli_list)

    absent_migrations = cli_list - {
        item.name for item in available_migrations}
    if absent_migrations:
        raise ValueError("Cannot find following migrations: {0}".format(
            sorted(absent_migrations)))

    return [item for item in available_migrations if item.name in cli_list]


def apply_migration(migration, *, ok=True):
    result = migration_script.MigrationState.ok
    if not ok:
        result = migration_script.MigrationState.failed

    LOG.info("Save result of %s migration (result %s)", migration.name, result)

    return migration_script.MigrationScript.create(
        migration.name, migration.script_hash, result,
        migration.stdout, migration.stderr
    )
