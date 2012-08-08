from bs.lib import constants
import ConfigParser, os, urllib2, tempfile, shutil

import tg
from zipfile import ZipFile as zip
main_section = 'main'
help_section = 'help'

def init_plugins():
    '''
    Init the plugin manager
    '''
    do_update = tg.config.get('plugins.update')
    if do_update and do_update.lower() in ['1', 'true', 't']:
        update()

    plug_dir = constants.plugin_directory()

    print ' --- init plugins located in %s ---' % plug_dir
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([plug_dir])

    manager.setCategoriesFilter({
        "Operations" : OperationPlugin,
        })
    manager.collectPlugins()
    cfg_file = constants.services_config_file()
    print ' --- write service config file %s --- ' % cfg_file
    write_config_file(cfg_file, manager)

    return manager



def _check_plugin_info(plug):
    if plug.info is None:
        raise Exception('You must provide info about your plugin.')
    if not plug.info.has_key('title'):
        raise Exception('you must provide a title for your plugin.')
    if not plug.info.has_key('description'):
        raise Exception('you must provide a description for your plugin.')
    if not plug.info.has_key('path'):
        raise Exception('you must an unique path for your plugin.')
    if not plug.info.has_key('output'):
        raise Exception('you must provide a graphical output for your plugin.')
    if not plug.info.has_key('in'):
        raise Exception('you must provide a description about input parameters used in your plugin.')
    if not plug.info.has_key('out'):
        raise Exception('you must provide a description about out parameters used in your plugin.')


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
        try:
            _check_plugin_info(po)
            config.set(main_section, po.title, po.unique_id())
        except Exception as e:
            print "Plugin %s not loaded : %s" % (po, e)


    with open(out, 'wb') as cf:
        config.write(cf)



def update():
    github_url = tg.config.get('plugins.github.url')
    print ' --- updating plugins from %s ---' % github_url
    # download
    req = urllib2.urlopen(github_url)
    tmp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False)
    tmp_file.write(req.read())
    tmp_file.close()

    #extract
    tmp_dir = tempfile.mkdtemp()
    z = zip(tmp_file.name)
    for info in z.infolist():
        f = info.filename
        dirname, fname = os.path.split(f)
        if dirname.endswith('plugins') and not fname == '' and not fname == '__init__.py':
            data = z.read(f)
            ext_name = os.path.split(f)[1]
            out_path = os.path.join(tmp_dir, ext_name)
            with open(out_path, 'wb') as out:
                out.write(data)

    #removing files from plugins directory
    plug_dir = constants.plugin_directory()
    shutil.rmtree(plug_dir, ignore_errors=True)

    #move new files to plugin directory
    os.mkdir(plug_dir)
    for plug in os.listdir(tmp_dir):
        shutil.move(os.path.join(tmp_dir, plug), plug_dir)

    #removing tmp files
    shutil.rmtree(tmp_dir)
    os.remove(tmp_file.name)



from plugin import temporary_path, OperationPlugin, BaseForm, retrieve_parameter, MultipleFileUpload