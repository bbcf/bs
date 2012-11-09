# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in bs.
This file complements development/deployment.ini.
Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
"""

from tg.configuration import AppConfig
import bs
from bs import model
from bs.lib import app_globals
from bs.lib import helpers

base_config = AppConfig()
base_config.renderers = []
base_config.package = bs
#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
base_config.renderers.append('mako')

# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')
#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession
base_config.use_transaction_manager = True
base_config.use_toscawidgets = False
base_config.use_toscawidgets2 = True

# HOOKS


def on_startup():
    import datetime
    print ' --- starting bs application --- ' + str(datetime.datetime.now())


def on_shutdown():
    print '--- stopping bs application --- '


def start_app(app):
    print ' --- import operations --- '
    import bs.operations
    return app

base_config.call_on_startup = [on_startup]
base_config.call_on_shutdown = [on_shutdown]
base_config.register_hook('before_config', start_app)
token = 'GDV'
