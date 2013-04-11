# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, response

from bs.lib.base import BaseController
from bs.controllers.error import ErrorController
from bs.controllers import DirectController, PluginController, JobController, DevController
from bs.lib.operations import wordlist
from bs.lib import operations
from bs.model import DBSession, Job, PluginRequest
from sqlalchemy.sql.expression import desc

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

    @expose('mako:bs.templates.visual_status')
    def index(self, *args, **kw):
        jobs = DBSession.query(Job).all()
        plugins = operations.get_plugins_path()
        mapping = {'plugins': plugins,
                   'ordered': operations.get_plugins_path(ordered=True),
                   'nbplugins': len(plugins),
                   'total': len(jobs),
                   'running': 0,
                   'failure': 0,
                   'pending': 0,
                   'success': 0}
        for job in jobs:
            if job.status.lower() == 'pending':
                print job.id
            mapping[job.status.lower()] += 1
        return mapping

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

    @expose('bs.templates.doc')
    def documentation(self):
        return {}

    @expose()
    def test(self, *a, **kw):
        print '%s, %s' % (a, kw)
        return ''

    @expose('bs.templates.koopa')
    def koopa(self, **kw):
        return {'koopa': kw.get('koopa', 'couac')}

    @expose()
    def troopa(self, *a, **kw):
        from pylons.templating import render_mako as render
        print render('bs/templates/koopa.mak', kw)
        return 'ok'
