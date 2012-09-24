# -*- coding: utf-8 -*-

"""Controllers for the bs application."""



from bs.controllers.visual import VisualController
from bs.controllers.request import RequestController
from bs.controllers.plugin import PluginController

from bs.controllers.root import RootController


import tg

def render_jsonp(tmpl_name, tmpl_vars, **kw):
    cb = str(tg.request.params.get('callback', 'callback'))
    for key in tg.render._get_tg_vars():
        del tmpl_vars[key]
    tg.response.headers['Content-Type'] = 'text/javascript'

    return '%s(%s)' % (cb, tg.json_encode(tmpl_vars))


from bs.config.app_cfg import base_config
base_config.render_functions['jsonp'] = render_jsonp
base_config.mimetype_lookup = {'.jsonp' : 'text/javascript'}