# -*- coding: utf-8 -*-
"""This module has different wrappers for the data structures."""


from __future__ import absolute_import
from __future__ import unicode_literals


class PaginationResult(object):
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
