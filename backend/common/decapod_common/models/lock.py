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
"""Each project which use MongoDB eventually comes to custom
in-house implementation of it's own MongoLock.

This project is not exceptional.
"""


import contextlib
import functools
import threading
import time
import uuid

import pymongo
import pymongo.errors

from decapod_common import exceptions
from decapod_common import log
from decapod_common import retryutils
from decapod_common import timeutils
from decapod_common.models import generic


LOG = log.getLogger(__name__)
"""Logger."""


class BaseMongoLock(generic.Base):

    COLLECTION_NAME = "lock"
    DEFAULT_PROLONG_TIMEOUT = 10  # seconds

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        cls.collection().create_index(
            [
                ("_id", generic.SORT_ASC),
                ("locker", generic.SORT_ASC)
            ],
            name="index_unique_locker",
            unique=True
        )

    def __init__(self, lockname):
        self.lockname = lockname
        self.lock_id = str(uuid.uuid4())
        self.acquired = False
        self.find_method = retryutils.mongo_retry()(
            self.collection().find_one_and_update
        )

    def acquire(self, *, block=True, timeout=None, force=False):
        if timeout is not None:
            timeout = abs(timeout)

        if force or not block:
            return self.try_to_acquire(force)

        if not timeout:
            while True:
                try:
                    return self.try_to_acquire()
                except exceptions.MongoLockCannotAcquire:
                    time.sleep(0.5)

        current_time = timeutils.timer()
        stop_at = current_time + timeout
        while current_time <= stop_at:
            current_time = timeutils.timer()
            try:
                return self.try_to_acquire()
            except exceptions.MongoLockCannotAcquire:
                time.sleep(0.5)

        raise exceptions.MongoLockCannotAcquire()

    def try_to_acquire(self, force=False):
        current_time = timeutils.current_unix_timestamp()
        query = {"_id": self.lockname}
        if not force:
            query["locker"] = None
            query["expired_at"] = {"$lte": current_time}

        try:
            self.find_method(
                query,
                {
                    "$set": {
                        "locker": self.lock_id,
                        "expired_at": current_time +
                        self.DEFAULT_PROLONG_TIMEOUT
                    }
                },
                upsert=True,
                return_document=pymongo.ReturnDocument.BEFORE
            )
        except pymongo.errors.PyMongoError as exc:
            raise exceptions.MongoLockCannotAcquire() from exc

        LOG.debug("Lock %s was acquire by locker %s",
                  self.lockname, self.lock_id)

        self.acquired = True

    def release(self, force=False):
        LOG.debug("Try to release lock %s by locker %s.",
                  self.lockname, self.lock_id)

        query = {"_id": self.lockname}
        if not force:
            query["locker"] = self.lock_id

        res = self.find_method(
            query, {"$set": {"expired_at": 0, "locker": None}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not res or res["expired_at"] != 0 or res["locker"] is not None:
            LOG.warning("Cannot release lock %s: %s", self.lockname, res)
            raise exceptions.MongoLockCannotRelease()

        self.acquired = False
        LOG.debug("Lock %s was released by locker %s.",
                  self.lockname, self.lock_id)

    def prolong(self, force=False):
        if not self.acquired and not force:
            LOG.warning("Cannot prolong mongo lock %s", self.lockname)
            raise exceptions.MongoLockCannotProlong()

        query = {"_id": self.lockname}
        if not force:
            query["locker"] = self.lock_id

        time_to_update = timeutils.current_unix_timestamp() + \
            self.DEFAULT_PROLONG_TIMEOUT
        result = self.find_method(
            query, {"$set": {"expired_at": time_to_update}},
            return_document=pymongo.ReturnDocument.AFTER
        )

        if not result or result["expired_at"] != time_to_update:
            LOG.warning("Cannot prolong mongo lock %s: %s",
                        self.lockname, result)
            raise exceptions.MongoLockCannotProlong()

        LOG.debug("Lock %s was proloned by locker %s.",
                  self.lockname, self.lock_id)


class AutoProlongMongoLock(BaseMongoLock):

    def __init__(self, lockname):
        super().__init__(lockname)

        self.prolonger_thread = None
        self.stop_event = threading.Event()

    def acquire(self, *, block=True, timeout=None, force=False):
        def prolonger():
            thread = threading.current_thread()
            sleep_timeout = self.DEFAULT_PROLONG_TIMEOUT / 2

            LOG.debug(
                "Prolong thread for locker %s of lock %s has been started. "
                "Thread %s, ident %s",
                self.lockname, self.lock_id, thread.name, thread.ident
            )

            self.stop_event.wait(sleep_timeout)
            while not self.stop_event.is_set():
                try:
                    self.prolong(force)
                except Exception as exc:
                    LOG.exception(
                        "Exception during prolonging of lock %s by locker "
                        "%s (prolonger thread %s, id=%d)",
                        self.lockname, self.lock_id,
                        thread.name, thread.ident
                    )
                self.stop_event.wait(sleep_timeout)

            LOG.debug(
                "Prolong thread for locker %s of lock %s has been stopped. "
                "Thread %s, ident %s",
                self.lockname, self.lock_id, thread.name, thread.ident
            )

        response = super().acquire(block=block, timeout=timeout, force=force)
        self.prolonger_thread = threading.Thread(
            target=prolonger,
            name="MongoLock prolonger {0} for {1}".format(
                self.lock_id, self.lockname),
            daemon=True
        )
        self.prolonger_thread.start()

        return response

    def release(self, force=True):
        self.stop_event.set()
        self.prolonger_thread.join()

        return super().release(force)


@contextlib.contextmanager
def with_mongolock_class(lock_cls, lockname, force=False, block=True,
                         timeout=None):
    lock = lock_cls(lockname)

    lock.acquire(block=block, timeout=timeout, force=force)
    try:
        yield lock
    finally:
        lock.release(force)


@contextlib.contextmanager
def with_base_lock(lockname, force=False, block=True, timeout=None):
    generator = with_mongolock_class(
        BaseMongoLock, lockname,
        force=force, block=block, timeout=timeout
    )
    with generator as lock:
        yield lock


@contextlib.contextmanager
def with_autoprolong_lock(lockname, force=False, block=True, timeout=None):
    generator = with_mongolock_class(
        AutoProlongMongoLock, lockname,
        force=force, block=block, timeout=timeout
    )
    with generator as lock:
        yield lock


def synchronized(lockname, force=False, block=True, timeout=None):
    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(*args, **kwargs):
            with with_autoprolong_lock(lockname, force, block, timeout):
                return func(*args, **kwargs)

        return inner_decorator
    return outer_decorator
