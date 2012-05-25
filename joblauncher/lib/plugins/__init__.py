from joblauncher.lib import constants
import ConfigParser, os

main_section = 'main'
help_section = 'help'


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

    cfg_file = constants.services_config_file()
    print ' --- write service config file %s --- ' % cfg_file
    write_config_file(cfg_file, manager)

    return manager






def write_config_file(out, plugin_mng):
    try :
        os.remove(out)
    except Exception :
        pass
    # read the configuration file
    config = ConfigParser.RawConfigParser()
    config.add_section(help_section)
    config.add_section(main_section)

    for plugin in plugin_mng.getAllPlugins():
        po = plugin.plugin_object
        config.set(main_section, po.unique_id(), po.files())
        config.set(help_section, po.unique_id(), '%s : %s' % (po.title().lower(), po.description()))
    with open(out, 'wb') as cf:
        config.write(cf)



