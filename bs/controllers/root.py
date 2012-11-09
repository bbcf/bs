# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, response
from bs.lib.base import BaseController
from bs.controllers import DirectController, RequestController, PluginController
import inspect
from sqlalchemy.orm import class_mapper
import bs.model.auth
from bs.operations import wordlist

__all__ = ['RootController']

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

    direct = DirectController()
    requests = RequestController()
    plugins = PluginController()

    @expose('mako:bs.templates.index')
    def index(self, *args, **kw):
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
        return {'page': 'vocabulary'}

    @expose('mako:bs.templates.dev')
    def developers(self):
        return {}
