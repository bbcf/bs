from joblauncher.lib import constants

def init_plugins():
    '''
    Init the plugin manager
    '''
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([constants.plugin_directory()])
    manager.collectPlugins()
    return manager












