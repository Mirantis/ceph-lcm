# -*- coding: utf-8 -*-
"""This module contains validators for different API calls."""


import jsonschema
import six

from cephlcm.api.exceptions import InvalidJSONError


def require_schema(schema):
    """This decorator verifies that request JSON matches given JSONSchema.

    http://json-schema.org
    """

    validator = jsonschema.Draft4Validator(schema)

    def outer_decorator(func):
        @six.wraps(func)
        def inner_decorator(self, *args, **kwargs):
            errors = validator.iter_errors(self.request_json)
            errors = [err.message for err in errors]

            if errors:
                raise InvalidJSONError(errors)

            return func(self, *args, **kwargs)

        return inner_decorator
    return outer_decorator
