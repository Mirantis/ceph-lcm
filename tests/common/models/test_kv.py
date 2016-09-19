# -*- coding: utf-8 -*-
"""Tests for cephlcm.models.kv."""


import pytest

from cephlcm_common.models import kv


def test_upsert_create(configure_model):
    namespace = pytest.faux.gen_alphanumeric()
    key = pytest.faux.gen_alpha()
    value = pytest.faux.gen_alphanumeric()

    new_model = kv.KV.upsert(namespace, key, value)
    assert new_model.namespace == namespace
    assert new_model.key == key
    assert new_model.value == value

    found_model = kv.KV.find_one(namespace, key)
    assert found_model.namespace == namespace
    assert found_model.key == key
    assert found_model.value == value


def test_upsert_renew(configure_model):
    namespace = pytest.faux.gen_alphanumeric()
    key = pytest.faux.gen_alpha()
    value = pytest.faux.gen_alphanumeric()
    value2 = pytest.faux.gen_alphanumeric()

    new_model = kv.KV.upsert(namespace, key, value)
    new_model2 = kv.KV.upsert(namespace, key, value2)
    assert new_model.namespace == new_model2.namespace
    assert new_model.key == new_model2.key
    assert new_model.value != new_model2.value

    found_model = kv.KV.find(namespace, [key])
    assert len(found_model) == 1
    found_model = found_model[0]

    assert found_model.value == new_model2.value
    assert found_model.value == value2


def test_remove(configure_model):
    keys = [pytest.faux.gen_alphanumeric() for _ in range(5)]
    namespace = pytest.faux.gen_alphanumeric()

    for key in keys:
        kv.KV.upsert(namespace, key, pytest.faux.gen_alphanumeric())

    assert len(kv.KV.find(namespace, keys)) == len(keys)
    kv.KV.remove(namespace, keys)

    assert kv.KV.find(namespace, keys) == []


def test_no_intersect(configure_model):
    key = pytest.faux.gen_alphanumeric()
    ns1 = pytest.faux.gen_alphanumeric()
    ns2 = pytest.faux.gen_alphanumeric()
    value1 = pytest.faux.gen_alpha()
    value2 = pytest.faux.gen_alpha()

    kv.KV.upsert(ns1, key, value1)
    kv.KV.upsert(ns2, key, value2)

    found_model1 = kv.KV.find_one(ns1, key)
    found_model2 = kv.KV.find_one(ns2, key)

    assert found_model1.value == value1
    assert found_model2.value == value2

    kv.KV.remove(ns1, [key])

    assert kv.KV.find_one(ns2, key)
    assert not kv.KV.find_one(ns1, key)
