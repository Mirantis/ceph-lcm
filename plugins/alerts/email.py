# -*- coding: utf-8 -*-
"""Email alerting plugin for CephLCM."""


import datetime
import pprint
import traceback

from cephlcm.common import config
from cephlcm.common import emailutils
from cephlcm.common import log


UNMANAGED_TEXT_MESSAGE = """
Unmanaged problem occured in application:

Date (UTC): {date}
RequestId:  {request_id}
Error:      {error!r}

Traceback:
{traceback}

Locals:
{locals}
""".strip()
"""Text message template to send on unmanaged exception."""

MANAGED_TEXT_MESSAGE = """
Problem in application:

Date (UTC):  {date}
RequestId:   {request_id}
Status Code: {error.code}
Description: {error.description}
""".strip()
"""Text message to send on managed exception."""

CONF = config.make_plugin_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


def alert(request_id, error, sys_exc_info):
    """Plugin entry point."""

    LOG.info("Email alerting on %s", error)

    if sys_exc_info[-1] is None:
        message = alert_managed_error(request_id, error)
        subject = "Internal server error"
    else:
        message = alert_unmanaged_error(request_id, error, sys_exc_info)
        subject = "Unmanaged internal server error"

    emailutils.send(CONF.ALERTS_EMAIL["send_to"], subject, message,
                    from_=CONF.ALERTS_EMAIL["from"])


def alert_managed_error(request_id, error):
    """Compose message about managed error."""

    return MANAGED_TEXT_MESSAGE.format(
        date=get_date(), request_id=request_id, error=error
    )


def alert_unmanaged_error(request_id, error, sys_exc_info):
    """Compose error on unmanaged error."""

    return UNMANAGED_TEXT_MESSAGE.format(
        date=get_date(),
        request_id=request_id,
        error=error,
        traceback=format_traceback(sys_exc_info),
        locals=format_locals(sys_exc_info)
    )


def format_traceback(sys_exc_info):
    """Formats traceback."""

    return "".join(traceback.format_tb(sys_exc_info[-1])).rstrip()


def format_locals(sys_exc_info):
    """Format locals for the frame where exception was raised."""

    current_tb = sys_exc_info[-1]
    while current_tb:
        next_tb = current_tb.tb_next
        if not next_tb:
            frame_locals = current_tb.tb_frame.f_locals
            return pprint.pformat(frame_locals)
        current_tb = next_tb


def get_date():
    """Returns a datetime when error happened."""

    return datetime.datetime.utcnow().isoformat()
