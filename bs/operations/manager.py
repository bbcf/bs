from bs.lib import constants
import wordlist, os, urllib2, tempfile, shutil, tg
from bs.operations.base import OperationPlugin
from bs.model import DBSession, Plugin
from bs.lib.plugin_manager import PluginManager

_loaded = False


def load_plugins():
    """
    Load the plugin into BioScript application
    """
    # update plugins from github
    do_update = tg.config.get('plugins.update')
    if do_update and do_update.lower() in ['1', 'true', 't']:
        _update(tg.config.get('plugins.github.url'))

    # initialize plugin manager with yapsy
    plug_dir = constants.plugin_directory()

    manager = PluginManager(restrict='bs-operation')
    manager.add_plugin_path(plug_dir)

    print ' --- init plugins located in %s ---' % plug_dir
    # from yapsy.PluginManager import PluginManager
    # manager = PluginManager()
    # manager.setPluginPlaces([plug_dir])
    # manager.setCategoriesFilter({
    #     "Operations": OperationPlugin,
    #     })

    # manager.collectPlugins()
    # check plugins and add in db if not already
    plugids = []
    for name, clazz in manager.plugins().iteritems():
        plug = clazz()
        #p = plug.plugin_object
        _check_plugin_info(plug)
        if tg.config['pylons.app_globals']:
            _check_in_database(plug)
        plugids.append(plug.unique_id())

    # check deprecated plugins
    if tg.config['pylons.app_globals']:
        for p in DBSession.query(Plugin).all():
            if p.generated_id not in plugids:
                p.deprecated = True
                DBSession.add(p)
        DBSession.flush()
    return manager


def _update(url):
    """
    Update plugins from a repository
    :param url: the url of the repository
    """

    print ' --- updating plugins from %s ---' % url
    from zipfile import ZipFile as zip

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
        if dirname.endswith('plugins') and not fname == '':
            data = z.read(f)
            ext_name = os.path.split(f)[1]
            out_path = os.path.join(tmp_dir, ext_name)
            with open(out_path, 'wb') as out:
                out.write(data)
    #removing files from plugins directory
    plug_dir = constants.plugin_directory()
    for f in os.listdir(plug_dir):
        if f != 'README' and f != '.gitignore':
            os.remove(os.path.join(plug_dir, f))

    #move new files to plugin directory
    for plug in os.listdir(tmp_dir):
        shutil.move(os.path.join(tmp_dir, plug), plug_dir)

    #removing tmp files
    shutil.rmtree(tmp_dir)
    os.remove(tmp_file.name)


def _check_in_database(plug):
    """
    Check if the plugin is in the database else create it
    """
    DB_plug = DBSession.query(Plugin).filter(Plugin.generated_id == plug.unique_id()).first()
    if DB_plug is None:
        DB_plug = Plugin()
        DB_plug.generated_id = plug.unique_id()
        DB_plug.deprecated = plug.deprecated
        info = plug.info
        DB_plug.info = {'title': info['title'],
                        'description': info['description'],
                        'path': info['path'],
                        'in': info['in'],
                        'out': info['out'],
                        'meta': info['meta']}
        DBSession.add(DB_plug)


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
