from joblauncher.lib.plugins import init_plugins
from joblauncher.lib.plugins import plugin


Manager = init_plugins()

def get_plugin_byId(_id):
    return plugin.get_plugin_byId(_id, manager=Manager)

def get_plugin_paths():
    return plugin.get_plugins_path(manager=Manager)