# -*- coding: utf-8 -*-
"""This module has db connection class."""


import pymongo

from cephlcm_common import config


CONF = config.make_config()
"""Config."""


class MongoDB:
    """Simple wrapper for MongoClient.

    This is require to support Flask-PyMongo way of DB referring.
    """

    def __init__(self, uri=None, connect=None, connect_timeout=None,
                 socket_timeout=None, pool_size=None):
        uri = uri if uri is not None else CONF.DB_URI
        connect = connect if connect is not None else CONF.DB_CONNECT
        connect_timeout = connect_timeout or CONF.DB_CONNECT_TIMEOUT
        socket_timeout = socket_timeout or CONF.DB_SOCKET_TIMEOUT
        pool_size = pool_size if pool_size is not None else CONF.DB_POOL_SIZE

        self.client = pymongo.MongoClient(
            uri, connect=connect, socketTimeoutMS=socket_timeout,
            connectTimeoutMS=connect_timeout, maxPoolSize=pool_size
        )
        self.dbname = self.client.get_default_database()
        self.dbname = self.dbname.name if self.dbname else "cephlcm"

    @property
    def db(self):
        return self.client[self.dbname]
