# -*- coding: utf-8 -*-

"""Error controller"""

from tg import request, expose

from joblauncher.lib.base import BaseController

from joblauncher.lib import constants

from joblauncher import model

from repoze.what.predicates import has_permission



__all__ = ['AdminController']





class AdminController(BaseController):

    allow_only = has_permission(constants.permission_admin_name)



    @expose('joblauncher.templates.admin')

    def index(self, *args, **kw):

        return {'page' : 'admin', 'admin_items' : [m.lower() for m in model.admin_models]}

