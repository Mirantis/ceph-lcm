# -*- coding: utf-8 -*-
"""This module has different wrappers for the data structures."""


import pymongo

from cephlcm_common import config


CONF = config.make_config()
"""Config."""


class PaginationResult:
    """PaginationResult wraps a data about a certain page in pagination."""

    def __init__(self, model_class, items, pagination):
        self.model_class = model_class
        self.items = items
        self.pagination = pagination
        self.total = items.count()

    def make_api_structure(self):
        """Makes API structure, converatable to JSON."""

        if self.pagination["all"]:
            return self.response_all()

        return self.response_paginated()

    def response_all(self):
        return {
            "total": self.total,
            "per_page": self.total,
            "page": 1,
            "items": list(self.modelize(self.items))
        }

    def response_paginated(self):
        items = self.items
        page_items_before = self.pagination["per_page"] \
            * (self.pagination["page"] - 1)
        if page_items_before:
            items = items.skip(page_items_before)
        items = items.limit(self.pagination["per_page"])

        return {
            "items": list(self.modelize(items)),
            "page": self.pagination["page"],
            "per_page": self.pagination["per_page"],
            "total": self.total
        }

    def modelize(self, items):
        for item in items:
            model = self.model_class()
            model.update_from_db_document(item)
            yield model.make_api_structure()


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
