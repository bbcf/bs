import os
import imp
import sys
import inspect
import pkgutil

RESERVED_FNAMES = ['__init__']
PLUGIN_EXTENSIONS = ['.py']

LLEVEL = 0


def debug(s, i=0):
    if LLEVEL > 0:
        print '%s%s' % ('\t' * i, s)


class PluginManager(object):

    def __init__(self, restrict=None):
        """
        Initialize the plugin manager.
        :param restrict: If restrict is set to a value, only class with
        the class parameter *pypl__restrict* set to the same value will be loaded.
        (it also can be a list)
        """

        self.paths = {}  # different paths used by th plugin manager
        self.paths['plugins'] = []  # path to the plugins
        self.__init_params()

        self.restrict = restrict  # restriction filter

    def __init_params(self):
        self._loaded_paths = []  # path that are already loaded
        self._loaded_plugins = {}  # loaded plugins
        self._plugins_ids = []  # reference all plugins name
        self._loaded = False  # loaded ?
        self.categories = {}

    def add_plugin_path(self, path):
        """
        Add a path to the plugin loader.
        :param path: the path to look on.
        """
        self.paths['plugins'].append(path)
        self._loaded = False

    def load(self):
        """
        Load plugins.
        """
        if self._loaded:
            self.unload()
        # look over paths and load classes, modules & packages
        for path in self.paths['plugins']:
            if path not in self._loaded_paths:
                root = os.path.split(path)[-1]
                self._loaded_paths.append(path)
                self._walk_plugins_paths(root, path)
        self._loaded = True

        # categorize
        for k, v in self._loaded_plugins.iteritems():
            if hasattr(v, 'bs_category'):
                attr = getattr(v, 'bs_category')
            else:
                attr = 'default'
            if attr not in self.categories:
                    self.categories[attr] = []
            self.categories[attr].append(k)

    def _walk_plugins_paths(self, root, path):
        """
        Recursively walk in directories to load all plugins that we can find.
        :param root: the root directory that was added to the plugin manager.
        :param path: the directory to walk in.
        """
        debug('Walk in %s (%s)' % (path, root))

        for loader, name, ispkg in pkgutil.iter_modules([path]):
            debug('Examine module %s %s %s' % (loader, name, ispkg), 1)
            mod_path = os.path.join(path, '%s.py' % name)
            mod_root = '%s.%s' % (root, name)
            if ispkg:
                self._walk_plugins_paths(mod_root, mod_path)
            else:
                # load classes
                fp, pathname, description = imp.find_module(name, [path])
                try:
                    mod = imp.load_module(name, fp, pathname, description)
                    clsmembers = inspect.getmembers(mod, inspect.isclass)
                    for name, clz in clsmembers:
                        if clz.__module__ == mod.__name__:
                            self._load_plugin(name, clz)
                except:
                    raise
                finally:
                    fp.close()

    def _load_plugin(self, name, clazz):
        debug('Loading %s (%s)' % (name, clazz), 2)
        if self._pass_restriction(clazz):
            plugid = name
            if hasattr(clazz, 'bs_identifier'):
                plugid = getattr(clazz, 'bs_identifier')

            # change plugin id if there is already one
            if plugid in self._loaded_plugins:
                debug('plugin id %s already exist' % plugid, 2)
                el = self._loaded_plugins.get(plugid)
                pid = '%s(%s)' % (el.__name__, el.__hash__(el))
                self._loaded_plugins[pid] = el
                del self._loaded_plugins[plugid]
                plugid = '%s(%s)' % (clazz.__name__, clazz.__hash__(clazz))
            # set plugin loaded
            debug('Loaded under %s ' % plugid, 3)
            self._loaded_plugins[plugid] = clazz

    def _verify_file_name(self, path):
        """
        Verify that the filen name is valid (no __init__, ended with .py, ...)
        :param path: the path to the file
        """
        fname, ext = os.path.splitext(os.path.split(path)[1])
        if fname in RESERVED_FNAMES or ext not in PLUGIN_EXTENSIONS:
            return False
        return True

    def _pass_restriction(self, element):
        """
        Look if the element (package, module or clazz) pass the restrict
        filter set (if there is one)
        :return a boolean
        """
        if not self.restrict:
            return True
        if hasattr(element, 'bs_plugin'):
            attr = getattr(element, 'bs_plugin')
            if isinstance(self.restrict, basestring) and attr == self.restrict:
                return True
            elif attr in self.restrict:
                return True
        return False

    def unload(self):
        """
        Unload all loaded plugins.
        Remove them from sys path.
        """
        for tag, value in self._plugins:
            for element in value:
                if element.__name__ in sys.modules:
                    del(sys.modules[element.__name__])
        self.__init_params()

    def plugins(self):
        if not self._loaded:
            self.load()
        return self._loaded_plugins

