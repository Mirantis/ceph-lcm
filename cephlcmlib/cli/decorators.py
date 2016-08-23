# -*- coding: utf-8 -*-
"""A list of decorators which are used in CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import os

import click
import six

from cephlcmlib import cli
from cephlcmlib import exceptions

try:
    import simplejson as json
except ImportError:
    import json


def catch_errors(func):
    """Decorator which catches all errors and tries to print them."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.CephLCMAPIError as exc:
            cli.format_output_json(ctx, exc.json, True)
        except exceptions.CephLCMError as exc:
            click.echo(six.text_type(exc), err=True)
        finally:
            ctx.close()

        ctx.exit(os.EX_SOFTWARE)

    return decorator


def with_client(func):
    """Decorator which pass both client and model client to method."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        kwargs["client"] = ctx.obj["client"]
        return func(*args, **kwargs)

    return decorator


def format_output(func):
    """Decorator which formats output."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        response = func(*args, **kwargs)
        if not response:
            return

        if ctx.obj["format"] == "json":
            cli.format_output_json(ctx, response)

    return decorator


def with_pagination(func):
    """Add pagination-related commandline options."""

    @six.wraps(func)
    @click.option(
        "--page", "-p",
        type=int,
        default=None,
        help="Page to request."
    )
    @click.option(
        "--per_page", "-r",
        type=int,
        default=None,
        help="How many items should be displayed per page."
    )
    @click.option(
        "--all",
        is_flag=True,
        help=(
            "Show all items, without pagination. "
            "Default behavior, 'page' and 'per_page' options disable this "
            "option."
        )
    )
    @click.option(
        "--list",
        is_flag=True,
        help="Remove pagination envelope, just list items."
    )
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        all_items = kwargs.pop("all", None)
        page = kwargs.pop("page", None)
        per_page = kwargs.pop("per_page", None)
        is_list = kwargs.pop("list", None)

        if all_items:
            query_params = {"all_items": "true"}
        else:
            query_params = {
                "page": page,
                "per_page": per_page
            }
        kwargs["query_params"] = query_params

        response = func(*args, **kwargs)
        if is_list:
            response = response["items"]

        return response

    return decorator


def model_edit(item_id, fetch_method_name, parse_json=True):
    """Adds '--edit-model' and 'model' flags.

    If '--edit-model' is set, user text editor will be launched. If no
    changes will be done, execution will be stopped. Edited text will be
    passed into decorated function as 'model' parameter.

    If 'model' is set, it will be considered as model itself.

    If 'parse_json' is True, text will be considered as JSON and parsed
    for you.
    """

    def outer_decorator(func):
        @six.wraps(func)
        @click.option(
            "--edit-model",
            is_flag=True,
            help="Fetch model and launch editor to fix stuff."
        )
        @click.option(
            "--model",
            default=None,
            type=cli.JSON,
            help=(
                "Full model data. If this parameter is set, other options "
                "won't be used. This parameter is JSON dump of the model."
            )
        )
        @with_client
        def inner_decorator(client, edit_model, model, *args, **kwargs):
            if not model:
                if edit_model:
                    fetch_function = getattr(client, fetch_method_name)
                    model = fetch_function(kwargs[item_id])
                    model = json.dumps(model, indent=4, sort_keys=True)
                    model = click.edit(model)
                    if not model:
                        return

            if model and parse_json and not isinstance(model, dict):
                model = json.loads(model)

            kwargs["model"] = model

            return func(*args, **kwargs)

        return inner_decorator
    return outer_decorator
