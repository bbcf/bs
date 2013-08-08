from bs.operations import manager as plmng
from operator import attrgetter, itemgetter

manager = plmng.load_plugins()
wordlist = manager.wordlist


def get_plugins_path(service=None, ordered=False):
    paths = _get_plugins_path(service, ordered)
    return paths


def _sort(l):
    return sorted(l, key=attrgetter('key'))


def _get_plugins_path(service, ordered):
    """
    Get the paths of the plugins
    """
    plugs = manager.plugins()
    if ordered in [True, 'T', 1, '1', 'true', 'True', 'ok', 't']:
        paths = _mix_plugin_paths(plugs, service)
        paths = paths._serialize()
    else:
        paths = []
        for pname, pclazz in plugs.iteritems():
            o = pclazz()
            node = Node(o.info['title'])
            node.id = o.unique_id()
            node.info = serialize_info(o)
            node = node._serialize()
            paths.append(node)
        paths = sorted(paths, key=itemgetter('key'))
    return paths


def serialize_info(plug):
    """
    Serialize plugin info in the node.
    """
    # take basic info
    inf = plug.info

    # add links to code and doc
    try:
        inf['html_doc'] = plug.html_doc_link()
        inf['html_src_code'] = plug.html_source_code_link()
    except Exception as e:
        print 'html_doc and html_src_code error'
        print e

    # set html description
    inf['desc_as_html'] = plug.description_as_html
    return inf

def restructuredtextToHtml(text):
    print text
    from docutils.core import publish_parts
    text = publish_parts(text, writer_name='html')['body']
    print '*********************************'
    print text
    return text

def get_plugin_byId(_id):
    '''
    Get a plugin by it's id
    '''
    plugs = manager.plugins()
    for pname, pclazz in plugs.iteritems():
        plug = pclazz()
        if plug.unique_id() == _id:
            return plug
    raise Exception('Plugin with id %s not found' % _id)


def _mix_plugin_paths(plugins, service=None):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on an interface.
    Check if all different before.
    '''
    nodes = []
    uids = []
    for pname, pclazz in plugins.iteritems():
        o = pclazz()
        uid = o.unique_id()
        if uid in uids:
            raise Exception('Path %s already exists' % o.info.get('path'))
        uids.append(uid)

    for pname, pclazz in plugins.iteritems():
        o = pclazz()
        if service is not None:
            from bs.lib.services import service_manager
            param = service_manager.get(service.name, 'operations', default=[])
            if not param:
                nodes.append(o)
            elif o.unique_id() in param:
                nodes.append(o)
        else:
            nodes.append(o)

    return _pathify(nodes)


class Node(object):
    def __init__(self, key):
        self.childs = []
        self.key = key
        self.id = None
        self.info = None
        self.html_doc = None

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
        if self.key is not None:
            d['key'] = self.key
        if self.id is not None:
            d['id'] = self.id
        if self.childs:
            d['childs'] = [child._serialize() for child in _sort(self.childs)]
        if self.id is not None:
            d['info'] = self._serialize_info()
        return d

    def _serialize_info(self):
        """
        Serialize the info parameter of a plugin
        """
        return dict((k, v) for k, v in self.info.iteritems() if k != 'output' and v is not None)


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
        else:
            new = p
            node.add(p)
        _mix(new, path, index + 1, uid, info)
    else:
        node.id = uid
        node.info = info


def _pathify(nodes):
    '''
    Mix plugin list together
    '''
    root = Node("Operations")
    for n in nodes:
        _mix(root, n.info['path'], 0, n.unique_id(), serialize_info(n))
    return root
