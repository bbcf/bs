def get_plugins_path(service=None, ordered=False):
    """
    Get the paths of the plugins
    """
    plugs = plugin_manager.getAllPlugins()
    if ordered in [True, 'T', 1, '1', 'true', 'True', 'ok', 't']:
        paths =_mix_plugin_paths(plugs, service)
        paths = paths._serialize()
    else :
        paths = []
        for plug in plugs:
            o = plug.plugin_object
            node = Node(None)
            node.id = o.unique_id()
            node.info = o.info
            node = node._serialize()
            paths.append(node)
    return paths



def get_plugin_byId(_id):
    '''
    Get a plugin by it's id
    '''
    plugs = plugin_manager.getAllPlugins()
    for p in plugs :
        if p.plugin_object.unique_id() == _id : return p
    raise Exception('Plugin with id %s not found' % _id)




















import hashlib, os, json, wordlist
from bs.lib import util



import string, random
from bs.operations import plugin_manager

random_name = lambda x : ''.join(random.choice(string.ascii_lowercase + string.digits) for i in xrange(x))

def temporary_path(fname=None, ext=None):
    tmp_dir = util.tmpdir()
    if fname is None : fname = random_name(6)
    if ext is not None:
        if ext.startswith('.') : fname += ext
        else :                   fname  = '%s.%s' % (fname, ext)
    fpath = os.path.join(tmp_dir, fname)
    return fpath

def list_plugins():
    for p in plugin_manager.getAllPlugins():
        print p







def _serialize_node():
    """
    Serialize
    """

def _mix_plugin_paths(plugins, service=None):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on an interface.
    Check if all different before.
    '''
    nodes = []
    uids = []
    for plug in plugins:
        o = plug.plugin_object
        uid = o.unique_id()
        if uid in uids: raise Exception('Path %s already exists' % o.info.path)
        uids.append(uid)

    for plug in plugins:
        o = plug.plugin_object
        if service is not None:
            from bs.lib.services import service_manager
            param = service_manager.get(service.name, 'operations', default=[])
            if not param:
                nodes.append(o)
            elif o.unique_id() in param:
                nodes.append(o)
        else :
            nodes.append(o)

    return _pathify(nodes)


class Node(object):
    def __init__(self, key):
        self.childs = []
        self.key = key
        self.id = None
        self.info = None

    def add(self, child):
        self.childs.append(child)

    def has_child(self, child):
        return self.childs.count(child) > 0

    def get_child(self, child):
        return self.childs[self.childs.index(child)]

    def __eq__(self, o):
        return self.key == o.key

    def _serialize(self):
        """
        Method that serialize a node object
        """
        d = {}
        if self.key is not None: d['key'] = self.key
        if self.id is not None: d['id'] = self.id
        if self.childs : d['childs'] = [child._serialize() for child in self.childs]
        if self.id is not None: d['info'] = self._serialize_info()
        return d

    def _serialize_info(self):
        """
        Serialize the info parameter of a plugin
        """
        return dict((k, v) for k, v in self.info.iteritems() if k!='output' and v is not None)

def encode_tree(obj):
    '''
    JSON function to make recursive nodes being JSON serializable
    '''
    if not isinstance(obj, Node):
        return
        #raise TypeError("%r is not JSON serializable" % (obj,))
    return dict((k, v) for k, v in obj.__dict__.iteritems() if v is not None)


def _mix(node, path, index, uid=None, info=None):
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
        _mix(new, path, index + 1, uid, info)

    else :
        node.id = uid
        node.info = info

def _pathify(nodes):
    '''
    Mix plugin list together
    '''
    root = Node("Operations")
    for n in nodes:
        _mix(root, n.info['path'], 0, n.unique_id(), n.info)
    return root



