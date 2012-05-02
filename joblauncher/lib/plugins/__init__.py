from joblauncher.lib import constants

def init_plugins():
    '''
    Init the plugin manager
    '''
    plug_dir = constants.plugin_directory()
    print ' --- init plugins located in %s ---' % plug_dir
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([plug_dir])
    manager.collectPlugins()
    return manager












