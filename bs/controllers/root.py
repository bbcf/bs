# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, response

from bs.lib.base import BaseController
from bs.controllers.error import ErrorController
from bs.controllers import DirectController, PluginController, JobController, DevController
from bs.operations import wordlist
__all__ = ['RootController']


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
    devs = DevController()
    jobs = JobController()
    plugins = PluginController()
    error = ErrorController()

    @expose('bs.templates.index')
    def index(self, *args, **kw):
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

    @expose('bs.templates.dev')
    def developers(self):
        return {}
