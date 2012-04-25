from joblauncher.lib import constants

def init_plugins():
    '''
    Init the plugin manager
    WARNING : celery daemon MUST run on the same server because of the plugins :
    plugins are identified by python hash method which differ between computers.
    If you want to put celery on another server, replace hash() method by the hashlib module.
    '''
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([constants.plugin_directory()])
    manager.collectPlugins()
    return manager












