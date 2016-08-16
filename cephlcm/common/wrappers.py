# -*- coding: utf-8 -*-
"""This module has different wrappers for the data structures."""


import pymongo

from cephlcm.common import config


CONF = config.make_config()
"""Config."""


class PaginationResult:
    """PaginationResult wraps a data about a certain page in pagination."""

    def __init__(self, model_class, items, pagination, total):
        self.model_class = model_class
        self.items = items
        self.pagination = pagination
        self.total = total

    def __iter__(self):
        for item in self.items:
            model = self.model_class()
            model.update_from_db_document(item)

            yield model

    def make_api_structure(self):
        """Makes API structure, converatable to JSON."""

        return {
            "items": [item.make_api_structure() for item in self],
            "page": self.pagination["page"],
            "per_page": self.pagination["per_page"],
            "total": self.total
        }


class MongoDBWrapper:
    """Simple wrapper for MongoClient.

    This is require to support Flask-PyMongo way of DB referring.
    """

    def __init__(self, host=None, port=None, dbname=None, connect=None):
        host = host or CONF.DB_HOST
        port = port or CONF.DB_PORT
        dbname = dbname or CONF.DB_DBNAME
        connect = connect if connect is not None else CONF.DB_CONNECT

        self.dbname = dbname
        self.client = pymongo.MongoClient(
            host=host, port=port, connect=connect
        )

    @property
    def db(self):
        return self.client[self.dbname]
