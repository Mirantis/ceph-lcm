# -*- coding: utf-8 -*-
"""Model for migration script."""


import hashlib
import os
import os.path
import subprocess

from shrimp_common import log


LOG = log.getLogger(__name__)
"""Logger."""


class MigrationScript:

    def __init__(self, path):
        self.path = path
        self.process = None
        self.stdout = ""
        self.stderr = ""

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def script_hash(self):
        hasher = hashlib.sha1()

        with open(self.path, "rb") as filefp:
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
            [self.path],
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
    files = [os.path.join(directory, name) for name in os.listdir(directory)]
    files = [name for name in files
             if os.path.isfile(name) and os.access(name, os.R_OK | os.X_OK)]
    files = sorted(files)

    return [MigrationScript(name) for name in files]
