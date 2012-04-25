from tg import app_globals
import hashlib

class OperationPlugin(object):

    uid = None
    """
    Inherit form this class to build your plugin.
    """
    def path(self):
        """
        Here define the path of your plugin : the succession of buttons which leads to the form apparition.
        Must return a list. The root is %s.
        ex : return ['Statistics', 'Base Coverage']
        This list will result in three buttons (with %s as first), then 'Statistics' and 'Base Coverage'
        the last that will make appears the form onClick.
        """ % (root_key, root_key)

        raise NotImplementedError('you must override this method in your plugin.')


    def title(self):
        '''
        Here you set the title of your form.
        ex : return 'My super title'
        '''

        raise NotImplementedError('you must override this method in your plugin.')

    def output(self):
        '''
        Here you must define the form to output when the user click on the last button you defined in the path property.
        The form are build using ToscaWidget0.9.
        ex :
        from pygdv.widgets.plugins import form
        return form.Example
        '''

        raise NotImplementedError('you must override this method in your plugin.')

    def process(self, **kw):
        '''
        Here you must define your function that will process the form parameters.
        ex : a simple method that add two parameters :
        return kw.get('param1', 0) + kw.get('param2', 0)
        '''

        raise NotImplementedError('you must override this method in your plugin.')

    def description(self):
        '''
        Here you can give a description to your job.
        '''
        raise NotImplementedError('you must override this method in your plugin.')

    def parameters(self):
        '''
        Here you can give the parameters needed for your job to run.
        '''
        raise NotImplementedError('you must override this method in your plugin.')

    def unique_id(self):
        '''
        It's an unique identifier for your plugin.
        Do not override
        '''
        if not self.uid:
            self.uid = hashlib.sha1(self.path().__str__()).hexdigest()
        return self.uid



def retrieve_parameter(params, param, default=None):
    return params.get(param, default)

def rp(params, param, default=None):
    return retrieve_parameter(params, param, default)




root_key = 'Operations'


def get_plugin_byId(_id):
    '''
    Get a plugin by it's id
    '''
    plugs = app_globals.plugin_manager.getAllPlugins()
    for p in plugs :
        if p.plugin_object.unique_id() == _id : return p
    return None


def get_plugins_path():
    """
    Get forms paths.
    """
    plugs = app_globals.plugin_manager.getAllPlugins()
    return _mix_plugin_paths(plugs)


def _mix_plugin_paths(plugins):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on an interface.
    '''
    nodes = []
    for plug in plugins:
        o = plug.plugin_object
        nodes.append(o)
    return _pathify(nodes)


class Node(object):
    def __init__(self, key):
        self.childs = []
        self.key = key
        self.id = None

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


def _mix(node, path, index, uid=None):
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
        _mix(new, path, index + 1, uid)
    else :
        node.id = uid

def _pathify(nodes):
    '''
    Mix a list of paths together
    '''
    root = Node(root_key)
    for n in nodes:
        _mix(root, n.path(), 0, n.unique_id())
    return root