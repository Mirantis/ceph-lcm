# -*- coding: utf-8 -*-
"""Commandline interface for migration scripts."""


import argparse
import sys
import time

import pkg_resources

from cephlcm_migration import migrators
from cephlcm_common import cliutils
from cephlcm_common import log
from cephlcm_common.models import migration_script


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

DIRECTORY = pkg_resources.resource_filename(
    "cephlcm_migration", "scripts")
"""Directory where migration scripts are placed."""

LOG = log.getLogger(__name__)
"""Logger."""


@cliutils.configure
def main():
    options = get_options()

    return options.callback(options)


def list_callback(options):
    for_listing = {}

    for item in migrators.get_migration_scripts(DIRECTORY):
        for_listing[item.name] = False
    for item in migration_script.MigrationScript.find():
        for_listing[item._id] = True

    for name, applied in sorted(for_listing.items()):
        if options.filter == "all":
            applied = "[applied]" if applied else "[not-applied]"
            applied = applied.ljust(len("[not-applied]"), " ")
            print("{0} {1}".format(applied, name))
        elif options.filter == "not_applied":
            if not applied:
                print(name)
        elif applied:
            print(name)


def apply_callback(options):
    migrations = get_migrations_to_apply(options)
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


def show_callback(options):
    all_migrations = migration_script.MigrationScript.find()
    all_migrations = {item._id: item for item in all_migrations}

    if options.migration not in all_migrations:
        raise Exception("Cannot find such migration.")

    migration = all_migrations[options.migration]
    message = MIGRATION_SHOW_TEMPLATE.format(
        name=migration._id,
        time=time.ctime(migration.time_executed),
        result=migration.state.name,
        script_hash=migration.script_hash,
        stdout=migration.stdout,
        stderr=migration.stderr
    )

    print(message)


def get_migrations_to_apply(options):
    avaialble_migrations = migrators.get_migration_scripts(DIRECTORY)
    db_migrations = migration_script.MigrationScript.find()
    db_migrations = {item._id for item in db_migrations}

    if not options.migration:
        if options.reapply:
            return avaialble_migrations
        if options.fake:
            for migr in avaialble_migrations:
                apply_migration(migr, ok=True)
            return []

        return [item for item in avaialble_migrations
                if item.name not in db_migrations]

    migration_names = set(options.migration)
    absent_migrations = migration_names - {
        item.name for item in avaialble_migrations}
    if absent_migrations:
        raise ValueError("Cannot find following migrations: {0}".format(
            sorted(absent_migrations)))
    migrations_to_apply = [
        item for item in avaialble_migrations if item.name in migration_names]

    if options.reapply:
        return migrations_to_apply

    if options.fake:
        for migr in migrations_to_apply:
            apply_migration(migr, ok=True)
        return []

    return [migr for migr in migrations_to_apply
            if migr.name not in db_migrations]


def apply_migration(migration, *, ok=True):
    result = migration_script.MigrationState.ok
    if not ok:
        result = migration_script.MigrationState.failed

    LOG.info("Save result of %s migration (result %s)", migration.name, result)

    return migration_script.MigrationScript.create(
        migration.name, migration.script_hash, result,
        migration.stdout, migration.stderr
    )


def get_options():
    parser = argparse.ArgumentParser(
        description="Run migrations again CephLCM database.")
    parser.set_defaults(callback=lambda el: parser.print_help())
    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser(
        "list", description="List migrations."
    )
    list_parser.set_defaults(callback=list_callback)
    list_parser.add_argument(
        "filter",
        help="Which migrations to show. Default 'all'.",
        choices=("all", "applied", "not_applied"),
        default="all"
    )

    apply_parser = subparsers.add_parser(
        "apply", description="Apply migration."
    )
    apply_parser.set_defaults(callback=apply_callback)
    apply_parser.add_argument(
        "-r", "--reapply",
        help="Reapply migrations.",
        action="store_true",
        default=False
    )
    apply_parser.add_argument(
        "-f", "--fake",
        help="Fake apply migration.",
        action="store_true",
        default=False
    )
    apply_parser.add_argument(
        "migration",
        nargs="*",
        help=(
            "Name of migration to apply. If nothing is given, all required "
            "migration will be applied. On reapply or fake all possible "
            "migration will be applied again."
        )
    )

    show_parser = subparsers.add_parser(
        "show", description="Show information on applied migration."
    )
    show_parser.set_defaults(callback=show_callback)
    show_parser.add_argument(
        "migration",
        help="Name of the migration to show."
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
