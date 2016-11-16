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
"""Model for migration script.

Basically, migration script is a script that intended to be used to
execute ad-hoc scripts on production installation. These scripts can
update database, apply new schema or rework data.
"""


import enum

from decapod_common import timeutils
from decapod_common.models import generic


@enum.unique
class MigrationState(enum.IntEnum):
    ok = 0
    failed = 1


class MigrationScript(generic.Base):

    COLLECTION_NAME = "migration_script"

    @classmethod
    def create(cls, name, script_hash, state, stdout, stderr,
               time_executed=None):
        if not time_executed:
            time_executed = timeutils.current_unix_timestamp()

        instance = cls()
        instance._id = name
        instance.script_hash = script_hash
        instance.state = state
        instance.time_executed = time_executed
        instance.stdout = stdout
        instance.stderr = stderr

        instance.save()

        return instance

    @classmethod
    def find(cls):
        documents = []
        sorter = [("_id", generic.SORT_ASC)]

        for item in cls.collection().find({}, sort=sorter):
            instance = cls()
            instance.update_from_db_document(item)
            documents.append(instance)

        return documents

    def __init__(self):
        self._id = ""
        self.script_hash = ""
        self.state = MigrationState.ok
        self.time_executed = 0
        self.stdout = ""
        self.stderr = ""

    def save(self):
        template = {
            "_id": self._id,
            "state": self.state.name,
            "script_hash": self.script_hash,
            "time_executed": self.time_executed,
            "stdout": self.stdout,
            "stderr": self.stderr
        }
        self.collection().find_one_and_replace(
            {"_id": template["_id"]},
            template,
            upsert=True
        )

    def update_from_db_document(self, structure):
        self._id = structure["_id"]
        self.script_hash = structure["script_hash"]
        self.state = MigrationState[structure["state"]]
        self.time_executed = structure["time_executed"]
        self.stdout = structure["stdout"]
        self.stderr = structure["stderr"]
