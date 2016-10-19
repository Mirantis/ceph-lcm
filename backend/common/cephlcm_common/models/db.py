# -*- coding: utf-8 -*-
"""This module has db connection class."""


import gridfs
import gridfs.errors
import pymongo

from cephlcm_common import config
from cephlcm_common import log


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class MongoDB:
    """Simple wrapper for MongoClient.

    This is require to support Flask-PyMongo way of DB referring.
    """

    def __init__(self, uri=None, connect=None, connect_timeout=None,
                 socket_timeout=None, pool_size=None):
        uri = uri if uri is not None else CONF["db"]["uri"]
        connect = connect if connect is not None else CONF["db"]["connect"]
        connect_timeout = connect_timeout or CONF["db"]["connect_timeout"]
        socket_timeout = socket_timeout or CONF["db"]["socket_timeout"]
        pool_size = pool_size if pool_size is not None \
            else CONF["db"]["pool_size"]

        self.client = pymongo.MongoClient(
            uri, connect=connect, socketTimeoutMS=socket_timeout,
            connectTimeoutMS=connect_timeout, maxPoolSize=pool_size
        )
        self.dbname = self.client.get_default_database()
        self.dbname = self.dbname.name if self.dbname else "cephlcm"

    @property
    def db(self):
        return self.client[self.dbname]


class FileStorage:

    COLLECTION = "fs"

    def __init__(self, db):
        self.fs = gridfs.GridFS(db, collection=self.COLLECTION)

    def delete(self, key):
        self.fs.delete(key)

    def __contains__(self, key):
        return self.fs.exists(key)

    def get(self, key):
        try:
            return self.fs.get(key)
        except (gridfs.errors.CorruptGridFile, gridfs.errors.NoFile) as exc:
            LOG.warning("Cannot find file %s in collection %s: %s",
                        key, self.COLLECTION, exc)

    def new_file(self, key, filename=None, content_type=None):
        kwargs = {"_id": key}
        if filename is not None:
            kwargs["filename"] = filename
        if content_type is not None:
            kwargs["content_type"] = content_type

        return self.fs.new_file(**kwargs)
