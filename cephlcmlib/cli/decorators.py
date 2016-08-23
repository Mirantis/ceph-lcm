# -*- coding: utf-8 -*-
"""A list of decorators which are used in CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import os

import click
import six

import cephlcmlib.cli
import cephlcmlib.exceptions


def catch_errors(func):
    """Decorator which catches all errors and tries to print them."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except cephlcmlib.exceptions.CephLCMAPIError as exc:
            cephlcmlib.cli.format_output_json(ctx, exc.json, True)
        except cephlcmlib.exceptions.CephLCMError as exc:
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
            cephlcmlib.cli.format_output_json(ctx, response)

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
