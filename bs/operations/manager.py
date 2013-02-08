import wordlist
from bs.model import DBSession, Plugin
import inspect
import sys
import imp
import os
import traceback

DEBUG_LEVEL = 1


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[plugin manager] %s%s' % ('\t' * t, s)


class PluginError(Exception):
    pass


class PluginManager(object):

    def __init__(self, modulename):
        self.plugs = {}
        self.modname = modulename
        self.module = None
        self.loaded = False

    def plugins(self):
        if not self.loaded:
            self.load()
        return self.plugs

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        self.module = __import__(self.modname)
        self.modpath = os.path.split(self.module.__file__)[0]
        debug('Loading plugins from %s.' % self.modpath)
        for pfile in self.module.PLUGINS_FILES:
            try:
                fp, pathname, description = imp.find_module(pfile, [self.modpath])
                try:
                    p = imp.load_module(pfile, fp, pathname, description)
                    clsmembers = inspect.getmembers(p, inspect.isclass)
                    for name, clz in clsmembers:
                        if clz.__module__ == p.__name__ and hasattr(clz, 'bs_plugin') and getattr(clz, 'bs_plugin') == 'bs-operation':
                            debug('loading %s' % pfile, 1)
                            if p.__name__ in self.plugs:
                                raise PluginError('Plugin with the same name : %s (%s) is already loaded : %s.' % (p.__name__, clz, self.plugs[p.__name__]))
                            self.plugs[p.__name__] = clz

                except Exception as e:
                    print '[e][plugin manager] Module %s not loaded cause : %s' % (pfile, str(e))
                    if DEBUG_LEVEL > 0:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        print '\n'.join(traceback.format_tb(exc_traceback))
                finally:
                    fp.close()
            except ImportError as e:
                print '[e][plugin manager] Module %s not found.' % pfile
        debug('loaded : %s' % ', '.join([k for k, v in self.plugs.iteritems()]))


def load_plugins():
    manager = PluginManager('bsPlugins')
    manager.load()
    return manager


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
        raise PluginError('You must provide info about your plugin.')
        # check if needed parameters are here
    if not 'title' in plug.info:
        raise PluginError('You must provide a title for your plugin.')
    if not 'description' in plug.info:
        raise PluginError('You must provide a description for your plugin.')
    if not 'path' in plug.info:
        raise PluginError('You must provide a unique path for your plugin.')
    if not 'in' in plug.info:
        raise PluginError('You must provide a description about input parameters used in your plugin.')
    if not 'output' in plug.info:
        _check_plugin_output(plug)
    if not 'out' in plug.info:
        raise PluginError('You must provide a description about out parameters used in your plugin.')

    # check if parameters are well described
    for param in plug.info.get('in') + plug.info.get('out'):
        if param.get('type') not in wordlist.wordlist.keys():
            raise PluginError('Param of type `%s` does not exist in %s' % (param.get('type'), wordlist.wordlist.keys()))


def _check_plugin_output(plug):
        output = plug.info.get('output', None)
        from bs.operations.form import generate_form
        if output is None:
            output = generate_form(plug.info.get('in', {}))
            plug.info['output'] = output
