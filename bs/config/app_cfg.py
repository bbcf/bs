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
from bs.lib import app_globals, helpers 

base_config = AppConfig()
base_config.renderers = []
base_config.prefer_toscawidgets2 = True

base_config.package = bs

#Enable json in expose
base_config.renderers.append('json')

#Enable genshi in expose to have a lingua franca for extensions and pluggable apps
#you can remove this if you don't plan to use it.
base_config.renderers.append('genshi')

#Set the default renderer
base_config.default_renderer = 'mako'
base_config.renderers.append('mako')
#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = bs.model
base_config.DBSession = bs.model.DBSession

import datetime


def on_startup():
    print ' --- starting bs webserver --- (%s)' % datetime.datetime.now()


def on_shutdown():
    print '--- stopping bs webserver --- (%s)' % datetime.datetime.now()


def start_app(app):
    print ' --- import operations --- '
    import bs.lib.operations
    print ' --- import services --- '
    import bs.lib.services
    return app

base_config.call_on_startup = [on_startup]
base_config.call_on_shutdown = [on_shutdown]
base_config.register_hook('before_config', start_app)
