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
"""Unittests for decapod_common.models."""


import pytest

from decapod_common.models import migration_script


@pytest.fixture
def ms_collection(configure_model):
    collection = migration_script.MigrationScript.collection()
    collection.remove({})

    return collection


@pytest.mark.parametrize("state", migration_script.MigrationState)
@pytest.mark.parametrize("time_executed", (None, 1))
def test_create(ms_collection, time_executed, state, freeze_time):
    name = pytest.faux.gen_alphanumeric()
    script_hash = pytest.faux.gen_alphanumeric()
    stdout = pytest.faux.gen_alphanumeric()
    stderr = pytest.faux.gen_alphanumeric()

    instance = migration_script.MigrationScript.create(
        name, script_hash, state, stdout, stderr, time_executed
    )

    db_model = list(ms_collection.find({}))
    assert len(db_model) == 1
    db_model = db_model.pop()

    assert instance._id == name
    assert instance.script_hash == script_hash
    assert instance.state == state
    if time_executed is None:
        assert instance.time_executed == int(freeze_time.return_value)
    else:
        assert instance.time_executed == time_executed
    assert instance.stdout == stdout
    assert instance.stderr == stderr

    assert db_model["_id"] == name
    assert db_model["script_hash"] == script_hash
    assert db_model["state"] == state.name
    if time_executed is None:
        assert db_model["time_executed"] == int(freeze_time.return_value)
    else:
        assert db_model["time_executed"] == time_executed
    assert db_model["stdout"] == stdout
    assert db_model["stderr"] == stderr


def test_save_again(ms_collection):
    instance = migration_script.MigrationScript.create(
        pytest.faux.gen_alphanumeric(),
        pytest.faux.gen_alphanumeric(),
        migration_script.MigrationState.ok,
        pytest.faux.gen_alphanumeric(),
        pytest.faux.gen_alphanumeric()
    )
    instance.save()

    assert ms_collection.find({}).count() == 1
    assert len(migration_script.MigrationScript.find()) == 1

    instance.script_hash = pytest.faux.gen_uuid()
    instance.save()

    assert ms_collection.find({}).count() == 1
    assert len(migration_script.MigrationScript.find()) == 1

    model = migration_script.MigrationScript.find()
    model = model.pop()
    assert model._id == instance._id
    assert instance.script_hash == model.script_hash
