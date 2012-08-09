from bs.lib.plugins import init_plugins
from bs.lib.plugins import plugin
from bs.lib import constants
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os


os.environ['CELERY_CONFIG_MODULE'] = 'celeryconfig'


### INIT PLUGINS ###
Manager = init_plugins()

def get_plugin_byId(_id):
    return plugin.get_plugin_byId(_id, manager=Manager)

def get_plugin_paths():
    return plugin.get_plugins_path(manager=Manager)

def init_plugins():
    '''
    Init the plugin manager
    WARNING : celery daemon MUST run on the same server because of the plugins :
    plugins are identified by python hash method which differ between computers.
    If you want to put celery on another server, replace hash() method by the haslib module.
    '''
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([constants.plugin_directory()])
    manager.collectPlugins()
    return manager


