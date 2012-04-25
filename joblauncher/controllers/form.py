# -*- coding: utf-8 -*-
from tg import request, expose, url
from tg.controllers import redirect
from joblauncher.lib.base import BaseController
from joblauncher.lib import constants, checker
from joblauncher.lib.plugins import plugin
from joblauncher import handler
from repoze.what.predicates import has_permission
import json

__all__ = ['FormController']





class FormController(BaseController):
    allow_only = has_permission(constants.permissions_read_name)


    @expose('json')
    @expose('joblauncher.templates.form_list')
    def list(self, *args, **kw):
        paths = plugin.get_plugins_path()
        operations_path = 'operations_path = %s' % json.dumps(plugin.get_plugins_path(), default=plugin.encode_tree)
        return {'page' : 'form', 'paths' : operations_path}

    @expose()
    def error(self, *args, **kw):
        return {'error' : 'bad request : %s ' % kw}



    @expose('joblaucher.templates.plugin_form')
    def index(self, id, *args, **kw):
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))

        user = handler.user.get_user_in_session(request)
        if not checker.authorized():
            raise redirect(url('./error', {'not authorized' : id}))

        obj = plug.plugin_object

        tmpl_context.form = obj.output()(action='./launch')

        # here put needed tmplcontexts

        return {'page' : 'form', 'title' : obj.title(), 'value' : kw}

    @expose()
    def launch(self, id, *args, **kw):

        plug = plugin.get_plugin_byId(id)
        form = plug.plugin_object.output()(action='validation')

        try:
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            flash(e, 'error')
            kw['id']=private_params.get('form_id')
            raise redirect(url('./index', kw))

        #tasks.plugin_process.delay(**kw)

        flash('Job launched')
        raise redirect(url('./done',  {}))

    @expose()
    def done(self, *args, **kw):
        return '%s, %s' % (args, kw)

    @expose('joblauncher.templates.form_info')
    def info(self, id):
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))

        user = handler.user.get_user_in_session(request)
        if not checker.authorized():
            raise redirect(url('./error', {'not authorized' : id}))

        o = plug.plugin_object
        info = o.description()
        title = o.title()
        params = o.parameters()
        return {'page' : 'form', 'info' : info, 'title' : title, 'parameters' : params}


