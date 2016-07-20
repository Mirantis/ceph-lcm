# -*- coding: utf-8 -*-
"""This module has different wrappers for the data structures."""


from __future__ import absolute_import
from __future__ import unicode_literals


class PaginationResult(object):
    """PaginationResult wraps a data about a certain page in pagination."""

    def __init__(self, page_data, current_page, total):
        self.page_data = page_data
        self.current_page = current_page
        self.total = total
