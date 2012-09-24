from bs.lib import constants
import wordlist, os, urllib2, tempfile, shutil
from bs.operations.base import OperationPlugin

_loaded = False


def load_plugins():
    """
    Load the plugin into BioScript application
    """
    # update plugins from github
    import tg
    do_update = tg.config.get('plugins.update')
    if do_update and do_update.lower() in ['1', 'true', 't']:
        _update(tg.config.get('plugins.github.url'))

    # initialize plugin manager with yapsy
    plug_dir = constants.plugin_directory()

    print ' --- init plugins located in %s ---' % plug_dir
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([plug_dir])
    manager.setCategoriesFilter({
        "Operations" : OperationPlugin,
        })
    manager.collectPlugins()
    _loaded = True

    # check plugins
    for plug in manager.getAllPlugins():
        p = plug.plugin_object
        _check_plugin_info(p)

    return manager





def _update(url):
    """
    Update plugins from a repository
    :param url: the url of the repository
    """

    print ' --- updating plugins from %s ---' % url
    # download
    req = urllib2.urlopen(url)
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













def _check_plugin_info(plug):
    if plug.info is None:
        raise Exception('You must provide info about your plugin.')
        # check if needed parameters are here
    if not plug.info.has_key('title'):
        raise Exception('you must provide a title for your plugin.')
    if not plug.info.has_key('description'):
        raise Exception('you must provide a description for your plugin.')
    if not plug.info.has_key('path'):
        raise Exception('you must an unique path for your plugin.')
    if not plug.info.has_key('in'):
        raise Exception('you must provide a description about input parameters used in your plugin.')
    if not plug.info.has_key('output'):
        _check_plugin_output(plug)
    if not plug.info.has_key('out'):
        raise Exception('you must provide a description about out parameters used in your plugin.')

    # check if parameters are well described
    for param in plug.info.get('in') +  plug.info.get('out'):
        if param.get('type') not in wordlist.wordlist.keys() :
            raise Exception('Param of type `%s` does not exist in %s' % (param.get('type'), wordlist.wordlist.keys()))


def _check_plugin_output(plug):
        output = plug.info.get('output', None)
        from bs.operations.form import generate_form
        if output is None:
            output = generate_form(plug.info.get('in', {}))
            plug.info['output'] = output
