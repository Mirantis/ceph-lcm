# -*- coding: utf-8 -*-
"""Tests for cephlcm.api.pagination."""


import json

import pytest

from cephlcm.api import pagination
from cephlcm.common import config


CONF = config.make_api_config()


def test_defaults():
    result = pagination.make_pagination({})

    assert result == {
        "page": 1,
        "per_page": CONF.API_PAGINATION_PER_PAGE,
        "filter": {},
        "sort_by": [],
        "all": False
    }


@pytest.mark.parametrize("value", (
    "", {}, [], "qq1", "1qq", -1, 0, None
))
@pytest.mark.parametrize("param", ("page", "per_page"))
def test_param_fail(param, value):
    params = {param: value}
    result = pagination.make_pagination(params)

    if param == "page":
        assert result[param] == 1
    else:
        assert result[param] == CONF.API_PAGINATION_PER_PAGE


@pytest.mark.parametrize("value", (
    1, "1", "1.0", 1.0, 1.5
))
@pytest.mark.parametrize("param", ("page", "per_page"))
def test_param_ok(param, value):
    params = {param: value}
    result = pagination.make_pagination(params)

    assert result[param] == int(float(value))


@pytest.mark.parametrize("value", (
    {}, [], "", "1", "11", {"p": {"regexp": 1}}
 ))
def test_parse_filter_fail(value):
    params = {"filter": json.dumps(value)}
    result = pagination.make_pagination(params)

    assert result["filter"] == {}


def test_parse_filter_ok():
    params = {
        "filter": {
            "a": {"gt": 1},
            "b": {"lt": 2},
            "c": {"lte": 3},
            "d": {"gte": 3},
            "e": {"gt": 1, "lt": 2},
            "f": {"gt": 1, "gte": 3},
            "j": {"regexp": "hello$"},
            "k": {"ne": "1"},
            "l": {"ne": 1},
            "m": {"eq": "1"},
            "n": {"eq": 1},
            "o": {"in": [1]},
            "p": {"in": ["2", "3"]},
            "q": "1",
            "r": 2
        }
    }
    params["filter"] = json.dumps(params["filter"])
    result = pagination.make_pagination(params)

    assert result["filter"]["a"] == {"$gt": 1}
    assert result["filter"]["b"] == {"$lt": 2}
    assert result["filter"]["c"] == {"$lte": 3}
    assert result["filter"]["d"] == {"$gte": 3}
    assert result["filter"]["e"] == {"$gt": 1, "$lt": 2}
    assert result["filter"]["f"] == {"$gt": 1, "$gte": 3}
    assert result["filter"]["j"].pattern == "hello$"
    assert result["filter"]["k"] == {"$ne": "1"}
    assert result["filter"]["l"] == {"$ne": 1}
    assert result["filter"]["m"] == {"$eq": "1"}
    assert result["filter"]["n"] == {"$eq": 1}
    assert result["filter"]["o"] == {"$in": [1]}
    assert result["filter"]["p"] == {"$in": ["2", "3"]}
    assert result["filter"]["q"] == "1"
    assert result["filter"]["r"] == 2


@pytest.mark.parametrize("value", (
    {}, [], "", "1", "11", {"eq": {}},
    {"param": {"eq": []}}, {"p": {"gt": ""}},
    {"p": {"gt": 1, "eq": 1}},
    {"p": {"regexp": 1}},
    {"q": 0}, {"q": -2}, {"q": 2}
 ))
def test_sort_by_fail(value):
    params = {"sort_by": json.dumps(value)}
    result = pagination.make_pagination(params)

    assert result["sort_by"] == []


def test_sort_by_ok():
    params = {"sort_by": json.dumps({"a": 1, "b": -1, "c": 1})}
    result = pagination.make_pagination(params)

    assert sorted(result["sort_by"]) == [("a", 1), ("b", -1), ("c", 1)]


@pytest.mark.parametrize("value", (
    "1", "y", "Y", "yes", "YES"
))
def test_query_all_true(value):
    params = {"all": value}
    result = pagination.make_pagination(params)

    assert result["all"]


@pytest.mark.parametrize("value", (
    "0", "n", "no", "NO",
    "", [], {}, 0
))
def test_query_all_false(value):
    params = {"all": value}
    result = pagination.make_pagination(params)

    assert not result["all"]
