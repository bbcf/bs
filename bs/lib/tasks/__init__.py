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


#### INIT DATABASE ###
#def init_model(url):
#    engine = create_engine(url, echo=False)
#    Session = sessionmaker(autoflush=False, autocommit=False, bind = engine)
#    return Session
#
#DBSession = init_model(conf['CELERY_RESULT_DBURI'])
#from bs.model.auth import User, Group
