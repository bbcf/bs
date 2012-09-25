# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, request, response, url
from bs.lib.base import BaseController
from bs.model import DBSession
from repoze.what.predicates import has_permission
from bs.controllers import VisualController, RequestController, PluginController
from bs import handler

__all__ = ['RootController']

import inspect, json
from sqlalchemy.orm import class_mapper
import bs.model.auth
from bs.operations import wordlist
models = {}

for m in bs.model.auth.__all__:
    m = getattr(bs.model.auth, m)
    if not inspect.isclass(m):
        continue
    try:
        mapper = class_mapper(m)
        models[m.__name__.lower()] = m
    except:
        pass

class RootController(BaseController):
    """
    The root controller for the bs application.
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    """

    visual = VisualController()
    requests = RequestController()
    plugins = PluginController()


    @expose('mako:bs.templates.index')
    def index(self,*args,**kw):
        return dict(page='index')

    

    @expose('bs.templates.index')
    def login_needed(self):
        flash('You need to login', 'error')
        return dict(page='index')




    @expose('json')
    def vocab(self, **kw):
        """
        Expose the controlled vocabulary
        """
        tag = kw.get('tag', 'def')
        if tag == 'def':
            response.content_type = "text/plain"
            return wordlist.definition
        if tag in ['incl', 'inclusion', 'inclusions', 'i']:
            return wordlist.inclusions
        if tag in ['wl', 'w', 'wordlist', 'words']:
            return wordlist.wordlist

    @expose('bs.templates.vocabulary')
    def vocabulary(self, **kw):
        return {'page' : 'vocabulary'}

    @expose('json')
    @expose('bs.templates.form_list')
    def list(self, *args, **kw):
        """
        Method to get the operations list
        """
        control = 'bs_redirect = %s; bs_operations_path = %s;' % (json.dumps(url('/form/index')), json.dumps(plugin.get_plugins_path(ordered=True)))

        return {'page' : 'form', 'bs_control' : control}


    @expose('json')
    def plugins_list(self, **kw):
        ordered = kw.get('ordered', False)
        user = handler.user.get_user_in_session(request)
        if user.is_service :
            d = {'plugins' : plugin.get_plugins_path(service=user, ordered=ordered)}
        else :
            d = {'plugins' : plugin.get_plugins_path(ordered=ordered)}
        return d

    @expose()
    def test_upload(self, *args, **kw):
        return {}


    @expose()
    def test(self):
        from bs.operations import plugin_manager
        for p in plugin_manager.getAllPlugins():
            print p
    

