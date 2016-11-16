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
"""This module has different wrappers for the data structures."""


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
