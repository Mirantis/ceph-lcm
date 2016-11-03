# -*- coding: utf-8 -*-
"""Shrimp CLI tools package."""


import warnings


# This is done to suppress Click warnings about unicode
warnings.simplefilter("ignore")


from shrimp_cli import cloud_config  # NOQA
from shrimp_cli import cluster  # NOQA
from shrimp_cli import execution  # NOQA
from shrimp_cli import password_reset  # NOQA
from shrimp_cli import permission  # NOQA
from shrimp_cli import playbook_configuration  # NOQA
from shrimp_cli import playbook  # NOQA
from shrimp_cli import role  # NOQA
from shrimp_cli import server  # NOQA
from shrimp_cli import user  # NOQA
