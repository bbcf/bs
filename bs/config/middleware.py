# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the bs application."""

from bs.config.app_cfg import base_config
from bs.config.environment import load_environment
import tw2.core
import os
import re
from webob import Request
from pkg_resources import resource_filename
htmlfilepattern = re.compile(r'(<html>.*<head>)(.*</head>.*<body>)(.*</html>)', re.DOTALL)

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


# custom middleware configuration
from tw2.core.middleware import TwMiddleware
from tw2.core import core
import webob as wo
import types
from tw2.core import resources, util
import re

find_charset = resources.find_charset


class _ResourceInjector(util.MultipleReplacer):

    def __init__(self):
        return util.MultipleReplacer.__init__(self, {
            r'<head(?!er).*?>': self._injector_for_location('head'),
            r'</head(?!er).*?>': self._injector_for_location(
                'headbottom', False
            ),
            r'<body.*?>': self._injector_for_location('bodytop'),
            r'</body.*?>': self._injector_for_location('bodybottom', False)
        }, re.I | re.M)

    def _injector_for_location(self, key, after=True):
        def inject(group, resources, encoding):
            inj = u'\n'.join([
                r.display(displays_on='string')
                for r in resources
                if r.location == key
            ])
            inj = inj.encode(encoding)
            if after:
                return group + inj
            return inj + group
        return inject

    def __call__(self, html, resources=None, encoding=None):
        if resources is None:
            resources = core.request_local().get('resources', None)
        if resources:
            toadd = ''
            popit = []
            for res in resources:
                if 'JSLink' in str(res):
                    # avoid jquery javascript to not override the main one
                    if not 'jquery' in res.filename:
                        resource_path = os.path.join(resource_filename(res.modname, ''), res.filename)
                         # some debug
                        # toadd += '<script type="text/javascript">'
                        # toadd += 'console.log("Log from custom middleware.");'
                        # toadd += 'console.log("{}");'.format(resource_path)
                        # toadd += '</script>'
                        with open(resource_path, 'r') as resource_file:
                            toadd += '<script type="text/javascript">'
                            toadd += resource_file.read()
                            toadd += '</script>'
                    popit.append(res)
            for topop in popit:
                resources.remove(topop)
            encoding = encoding or find_charset(html) or 'utf-8'
            # add css
            html = util.MultipleReplacer.__call__(
                self, html, resources, encoding
            )

            # add toadd (js files)
            one, two, three = htmlfilepattern.match(html).groups()
            html = one + two + toadd + three
            core.request_local().pop('resources', None)
        return html

# Bind __call__ directly so docstring is included in docs
inject_resources = _ResourceInjector().__call__


class CustomMiddleware(TwMiddleware):
    def __call__(self, environ, start_response):
        rl = core.request_local()
        rl.clear()
        rl['middleware'] = self
        req = wo.Request(environ)

        path = req.path_info
        if self.config.serve_resources and \
           path.startswith(self.config.res_prefix):
            return self.resources(environ, start_response)
        else:
            if self.config.serve_controllers and \
               path.startswith(self.config.controller_prefix):
                resp = self.controllers(req)
            else:
                if self.app:
                    resp = req.get_response(self.app, catch_exc_info=True)
                else:
                    resp = wo.Response(status="404 Not Found")

            ct = resp.headers.get('Content-Type', 'text/plain').lower()

            should_inject = (
                self.config.inject_resources
                and 'html' in ct
                and not isinstance(resp.app_iter, types.GeneratorType)
            )
            if should_inject:
                body = inject_resources(
                    resp.body,
                    encoding=resp.charset,
                )
                if isinstance(body, unicode):
                    resp.unicode_body = body
                else:
                    resp.body = body
        core.request_local().clear()
        return resp(environ, start_response)


def make_middleware(app=None, config=None, **kw):
    config = (config or {}).copy()
    config.update(kw)
    app = CustomMiddleware(app, **config)
    return app


#base_config.toscawidgets.framework.middleware.render_filter = render_filter

def wrapper_middleware(app):
    print 'wrapping'
    print app
    return app


class MyMiddleware(object):

    def __init__(self, wrap_app):
        self.wrap_app = wrap_app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            #headers.append(('Content-Length', "1"))
            return start_response(status, headers, exc_info)
        return self.wrap_app(environ, custom_start_response)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set bs up with the settings found in the PasteDeploy configuration
    file used.

    :param global_conf: The global settings for bs (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The bs application with all the relevant middleware
        loaded.

    This is the PasteDeploy factory for the bs application.

    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.


    """
    inject_resources = True
    serve_resources = True
    if 'prefix' in app_conf:
        custom = lambda app: make_middleware(app, serve_resources=serve_resources, inject_resources=inject_resources, res_prefix=app_conf['prefix'] + '/tw2/resources/', default_engine='mako')
    else:
        custom = lambda app: make_middleware(app, serve_resources=serve_resources, inject_resources=inject_resources, default_engine='mako')
    app = make_base_app(global_conf, wrap_app=custom, full_stack=True, **app_conf)
    #app = make_base_app(global_conf, full_stack=True, **app_conf)

    # Wrap your base TurboGears 2 application with custom middleware here

    app = MyMiddleware(app)
    return app


# from tg.configuration import AppConfig
# from tw.api import make_middleware as tw_middleware


# class MyAppConfig(AppConfig):

#     def add_tosca2_middleware(self, app):

#         app = tw_middleware(app, {
#             'toscawidgets.middleware.inject_resources': False,
#             })
#         return app

# base_config = MyAppConfig()
