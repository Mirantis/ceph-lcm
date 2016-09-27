# -*- coding: utf-8 -*-
"""Different endpoints should be used as a cron scripts."""


import functools
import time

from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common import timeutils
from cephlcm_common import wrappers
from cephlcm_common.models import generic
from cephlcm_common.models import token
from cephlcm_common.models import task


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


def configure(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        log.configure_logging(CONF.logging_config)
        generic.configure_models(wrappers.MongoDBWrapper())

        return func(*args, **kwargs)

    return decorator


@configure
def clean_expired_tokens():
    """This function swipe out expired tokens from DB."""

    timestamp = timeutils.current_unix_timestamp()

    result = token.TokenModel.collection().delete_many(
        {"expires_at": {"$lt": timestamp}}
    )

    LOG.info(
        "Clean expired tokens. Removed all tokens pre %d (%s). "
        "Cleaned %d tokens.",
        timestamp, time.ctime(timestamp), result.deleted_count
    )


@configure
def clean_old_tasks():
    """This function removes old finished tasks from database."""

    timestamp = timeutils.current_unix_timestamp()
    old_limit = timestamp - CONF.CRON_CLEAN_FINISHED_TASKS_AFTER_SECONDS
    limit_condition = {"$gt": 0, "$lte": old_limit}
    query = {
        "$or": [
            {"time.completed": limit_condition},
            {"time.cancelled": limit_condition},
            {"time_failed": limit_condition}
        ]
    }

    result = task.Task.collection().delete_many(query)

    LOG.info(
        "Clean old tasks. Removed all tasks pre %d (%s). Cleaned %d tasks.",
        old_limit, time.ctime(old_limit), result.deleted_count
    )
