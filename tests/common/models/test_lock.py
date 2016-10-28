# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.models.lock."""


import pytest

from cephlcm_common import exceptions
from cephlcm_common.models import lock


@pytest.fixture
def lock_collection(configure_model):
    collection = lock.BaseMongoLock.collection()
    collection.remove()

    return collection


@pytest.yield_fixture
def base_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    with lock.with_base_lock(lockname) as mongolock:
        yield mongolock


def test_acquire_empty_collection(base_lock, freeze_time, lock_collection):
    assert base_lock.lock_id
    assert base_lock.lockname
    assert base_lock.acquired

    db_model = lock_collection.find_one({"_id": base_lock.lockname})
    assert db_model
    assert db_model["locker"] == base_lock.lock_id
    assert db_model["expired_at"] >= int(freeze_time.return_value)


def test_check_release(freeze_time, lock_collection):
    lockname = pytest.faux.gen_alphanumeric()

    with lock.with_base_lock(lockname):
        pass

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] is None
    assert db_model["expired_at"] == 0


def test_check_double_acquire(lock_collection, no_sleep, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    with pytest.raises(exceptions.MongoLockCannotAcquire):
        lock2.acquire(block=False)

    freeze_time.side_effect = range(110, 120)

    def sleep_side_effect(*args, **kwargs):
        freeze_time.return_value += 1

    no_sleep.side_effect = sleep_side_effect

    with pytest.raises(exceptions.MongoLockCannotAcquire):
        lock2.acquire(block=True, timeout=5)


@pytest.mark.parametrize("block", (True, False))
def test_force_acquire_lock(block, lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    lock2.acquire(block=block, force=True, timeout=1)

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] == lock2.lock_id


def test_acquire_lock_after_wait(lock_collection, freeze_time, no_sleep):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    frst_expired_at = lock_collection.find_one({"_id": lockname})["expired_at"]

    freeze_time.side_effect = range(110, 120)

    def sleep_side_effect(*args, **kwargs):
        freeze_time.return_value += 1
        lock1.release()

    no_sleep.side_effect = sleep_side_effect

    lock2.acquire(block=True)
    assert lock2.acquired

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] == lock2.lock_id
    assert db_model["expired_at"] > frst_expired_at


def test_release_other_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    with pytest.raises(exceptions.MongoLockCannotRelease):
        lock2.release()


def test_force_release_other_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    lock2.release(force=True)
    assert not lock2.acquired
    assert lock1.acquired

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] is None
    assert db_model["expired_at"] == 0


def test_double_release_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    lock1.release()
    lock1.release(True)

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] is None
    assert db_model["expired_at"] == 0


@pytest.mark.parametrize("force", (True, False))
def test_prolong_lock(force, lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    freeze_time.return_value *= 2
    lock1.prolong(force)

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] == lock1.lock_id
    assert db_model["expired_at"] == int(freeze_time.return_value) + \
        lock.BaseMongoLock.DEFAULT_PROLONG_TIMEOUT


def test_other_prolong_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    freeze_time.return_value *= 2
    with pytest.raises(exceptions.MongoLockCannotProlong):
        lock2.prolong()


def test_force_prolong_lock(lock_collection, freeze_time):
    lockname = pytest.faux.gen_alphanumeric()
    lock1 = lock.BaseMongoLock(lockname)
    lock2 = lock.BaseMongoLock(lockname)

    lock1.acquire()
    freeze_time.return_value *= 2
    lock2.prolong(True)

    db_model = lock_collection.find_one({"_id": lockname})
    assert db_model
    assert db_model["locker"] == lock1.lock_id
    assert db_model["expired_at"] == int(freeze_time.return_value) + \
        lock.BaseMongoLock.DEFAULT_PROLONG_TIMEOUT
