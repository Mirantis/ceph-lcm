# -*- coding: utf-8 -*-
"""Different endpoints should be used as a cron scripts."""


import time

from cephlcm_common import cliutils
from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common import timeutils
from cephlcm_common.models import password_reset
from cephlcm_common.models import task
from cephlcm_common.models import token


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@cliutils.configure
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


@cliutils.configure
def clean_old_tasks():
    """This function removes old finished tasks from database."""

    timestamp = timeutils.current_unix_timestamp()
    old_limit = timestamp - CONF["cron"]["clean_finished_tasks_after_seconds"]
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


@cliutils.configure
def clean_expired_password_resets():
    """This function swipes expired password reset tokens from DB."""

    timestamp = timeutils.current_unix_timestamp()
    result = password_reset.PasswordReset.collection().delete_many(
        {"expires_at": {"$lt": timestamp}}
    )

    LOG.info(
        "Clean expired password reset tokens. Removed all tokens pre %d (%s). "
        "Cleaned %d tokens.",
        timestamp, time.ctime(timestamp), result.deleted_count
    )
