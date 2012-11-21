# -*- coding: utf-8 -*-
"""Setup the bs application"""

import logging
from tg import config
from bs import model
import transaction

def bootstrap(command, conf, vars):
    """Place any commands to setup bs here"""

    # <websetup.bootstrap.before.auth

    # <websetup.bootstrap.after.auth>
