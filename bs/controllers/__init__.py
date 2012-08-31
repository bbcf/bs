# -*- coding: utf-8 -*-

"""Controllers for the bs application."""



from bs.controllers.error import ErrorController
from bs.controllers.login import LoginController
from bs.controllers.group import GroupController
from bs.controllers.permission import PermissionController
from bs.controllers.user import UserController
from bs.controllers.admin import AdminController
from bs.controllers.form import FormController
from bs.controllers.request import RequestController

from bs.controllers.root import RootController



from tg import json_encode, response, request
from tg.render import _get_tg_vars

def render_jsonp(tmpl_name, tmpl_vars, **kw):
    cb = str(request.params.get('callback', 'callback'))
    for key in _get_tg_vars():
        del tmpl_vars[key]
    response.headers['Content-Type'] = 'text/javascript'
    return '%s(%s)' % (cb, json_encode(tmpl_vars))

from bs.config.app_cfg import base_config
base_config.render_functions['jsonp'] = render_jsonp
base_config.mimetype_lookup = {'.jsonp' : 'text/javascript'}