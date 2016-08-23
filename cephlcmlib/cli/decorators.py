# -*- coding: utf-8 -*-
"""A list of decorators which are used in CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import os

import click
import six

from cephlcmlib import exceptions
from cephlcmlib.cli import utils
from cephlcmlib.cli import param_types


def catch_errors(func):
    """Decorator which catches all errors and tries to print them."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.CephLCMAPIError as exc:
            utils.format_output_json(ctx, exc.json, True)
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
            utils.format_output_json(ctx, response)

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
        "--all", "-a",
        is_flag=True,
        help=(
            "Show all items, without pagination. "
            "Default behavior, 'page' and 'per_page' options disable this "
            "option."
        )
    )
    @click.option(
        "--list", "-l",
        type=click.Choice(["active", "archived", "all"]),
        default="active",
        help="List only certain class of elements. 'active' is default."
    )
    @click.option(
        "--sort-by", "-s",
        default="",
        type=param_types.SORT_BY,
        help=(
            "Comma-separated list of fieldnames for sorting. To define "
            "direction, please put '-' or '+' before name ('+' explicitly "
            "means). For example: 'time_deleted,-name,+version' means "
            "that sorting will be done by tuple (time_deleted ASC, "
            "name DESC, version ASC)"
        )
    )
    @click.option(
        "--no-envelope", "-n",
        is_flag=True,
        help=(
            "Remove pagination envelope, just list items. If all items "
            "requested, this implicitly meant."
        )
    )
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        all_items = kwargs.pop("all", None)
        page = kwargs.pop("page", None)
        per_page = kwargs.pop("per_page", None)
        no_envelope = kwargs.pop("no_envelope", None)
        list_elements = kwargs.pop("list", "active")
        sort_by = kwargs.pop("sort_by", {})

        all_items = all_items or not (page or per_page)
        no_envelope = all_items or no_envelope

        if all_items:
            query_params = {"all_items": True}
        else:
            query_params = {
                "page": page,
                "per_page": per_page
            }

        query_params["filter"] = {}
        if list_elements == "all":
            query_params["filter"]["time_deleted"] = {
                "ne": "unreal_value"
            }
        elif list_elements == "archived":
            query_params["filter"]["time_deleted"] = {
                "ne": 0
            }
        else:
            del query_params["filter"]

        if sort_by:
            query_params["sort_by"] = sort_by

        kwargs["query_params"] = query_params

        response = func(*args, **kwargs)
        if no_envelope:
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
            "--model-editor",
            is_flag=True,
            help="Fetch model and launch editor to fix stuff."
        )
        @click.option(
            "--model",
            default=None,
            type=param_types.JSON,
            help=(
                "Full model data. If this parameter is set, other options "
                "won't be used. This parameter is JSON dump of the model."
            )
        )
        @click.option(
            "--model-stdin",
            is_flag=True,
            help="Slurp model from stdin."
        )
        @click.pass_context
        def inner_decorator(ctx, model_stdin, model_editor, model,
                            *args, **kwargs):
            if not model:
                if model_stdin:
                    stream = click.get_text_stream("stdin")
                    model = "".join(stream)
                elif model_editor:
                    fetch_function = getattr(ctx.obj["client"],
                                             fetch_method_name)
                    model = fetch_function(kwargs[item_id])
                    model = utils.json_dumps(model)
                    model = click.edit(model)
                if not model:
                    return

            if model and parse_json and not isinstance(model, dict):
                if isinstance(model, bytes):
                    model = model.decode("utf-8")
                model = utils.json_loads(model)

            kwargs["model"] = model

            return func(*args, **kwargs)

        return inner_decorator
    return outer_decorator


def command(command_class, paginate=False):
    """Decorator to group generic parameters used everywhere."""

    def decorator(func):
        func = with_client(func)
        if paginate:
            func = with_pagination(func)
        func = format_output(func)
        func = catch_errors(func)

        name = utils.parameter_name(func.__name__)
        func = command_class.command(name=name)(func)

        return func

    return decorator
