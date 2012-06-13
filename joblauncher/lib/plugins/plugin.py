from tg import app_globals
import hashlib, tempfile, os
from joblauncher.lib import util

class OperationPlugin(object):

    uid = None
    def title(self):
        """
        A name for the Operation.
        """
        raise NotImplementedError('you must override this method (title) in your plugin.')

    def description(self):
        """
        A quick description about your operation.
        """
        raise NotImplementedError('you must override this method (description) in your plugin.')


    def path(self):
        """
        An unique path among all plugins.
        """
        raise NotImplementedError('you must override this method (path) in your plugin.')

    def output(self):
        """
        An output form (Toscawidget, Sprox).
        """
        raise NotImplementedError('you must override this method (output) in your plugin.')

    def parameters(self):
        """
        Operation parameters. A dict with the input(s) and output(s).
        """
        raise NotImplementedError('you must override this method (parameters) in your plugin.')

    def files(self):
        """
        The list of "in" parameters that are files.
        """
        return []

    def meta(self):
        """
        A dict with additional information. Put here everything you want.
        """
        return {}



    def process(self, **kw):
        """
        Here you must define your function that will process the form parameters.
        """
        raise NotImplementedError('you must override this method (process) in your plugin.')

    def unique_id(self):
        '''
        It's an unique identifier for your plugin.
        Do not override
        '''
        if not self.uid:
            self.uid = hashlib.sha1(self.path().__str__()).hexdigest()
        return self.uid

    def _pre_process(self, service_name):
        """
        Initializing plugin parameters
        """
        self.service = service_name
        self.files = []



# Some useful functions

def retrieve_parameter(params, param, default=None):
    """
    Retrieve the parameter form the form
    """
    p = params.get(param, default)
    if p == '' : return default
    return p

def new_file(plugin, file_path, out_param):
    ftype = plugin.parameters().get('out').get(out_param)
    plugin.files.append([file_path, ftype])


def nf(plugin, filename, out_param):
    return new_file(plugin, filename, out_param)

def rp(params, param, default=None):
    """
    Retrieve the parameter form the form
    """
    return retrieve_parameter(params, param, default)




def temporary_path(fname=None, ext=None):
   return util.temporary_path(fname=fname, ext=ext, dir=os.getcwd())





root_key = 'Operations'


def get_plugin_byId(_id, manager=None):
    '''
    Get a plugin by it's id
    '''
    if manager is None:
        manager = app_globals.plugin_manager
    plugs = manager.getAllPlugins()
    for p in plugs :
        if p.plugin_object.unique_id() == _id : return p
    return None


def get_plugins_path(manager=None, service=None):
    """
    Get forms paths.
    """
    if manager is None:
        manager = app_globals.plugin_manager
    plugs = manager.getAllPlugins()
    print plugs
    return _mix_plugin_paths(plugs, service)


def _mix_plugin_paths(plugins, service=None):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on an interface.
    '''
    nodes = []
    for plug in plugins:
        o = plug.plugin_object
        if service is not None:
            from joblauncher.lib.services import service_manager
            param = service_manager.get(service.name, 'operations')
            if o.unique_id() in param:
                nodes.append(o)
        else :
            nodes.append(o)

    return _pathify(nodes)


class Node(object):
    def __init__(self, key):
        self.childs = []
        self.key = key
        self.id = None
        self.fl = None

    def add(self, child):
        self.childs.append(child)

    def has_child(self, child):
        return self.childs.count(child) > 0

    def get_child(self, child):
        return self.childs[self.childs.index(child)]

    def __eq__(self, o):
        return self.key == o.key

        # def __repr__(self, *args, **kwargs):
        #     return '<%s childs : %s >' % (self.key ,self.childs)

def encode_tree(obj):
    '''
    JSON function to make recursive nodes being JSON serializable
    '''
    if not isinstance(obj, Node):
        raise TypeError("%r is not JSON serializable" % (obj,))
    return obj.__dict__


def _mix(node, path, index, uid=None, files_list=None):
    '''
    Mix path with the node
    '''
    if(index < len(path)):
        p = Node(path[index])
        if node.has_child(p):
            new = node.get_child(p)
        else :
            new = p
            node.add(p)
        _mix(new, path, index + 1, uid, files_list)
    else :
        node.id = uid
        node.fl = files_list

def _pathify(nodes):
    '''
    Mix a list of paths together
    '''
    root = Node(root_key)
    for n in nodes:
        _mix(root, n.path(), 0, n.unique_id(), n.files())
    return root






from tw import forms as twf
from tw.forms import validators as twv




import tw2.core
import tw2.forms

class BaseForm(tw2.forms.TableForm):
    pp = tw2.forms.HiddenField()
    key = tw2.forms.HiddenField()
    up = tw2.forms.HiddenField()

