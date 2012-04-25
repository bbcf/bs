# -*- coding: utf-8 -*-
from tg import request, expose, url, flash
from tg.controllers import redirect
from joblauncher.lib.base import BaseController
from joblauncher.lib import constants, checker
from joblauncher.lib.plugins import plugin
from joblauncher import handler
from repoze.what.predicates import has_permission
import json
from pylons import tmpl_context
from formencode import Invalid

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



    @expose('joblauncher.templates.plugin_form')
    def index(self, id, *args, **kw):
        print '[x] INDEX id %s, %s, %s' % (id, args, kw)
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))

        user = handler.user.get_user_in_session(request)
        if not checker.authorized():
            raise redirect(url('./error', {'not authorized' : id}))

        obj = plug.plugin_object

        tmpl_context.form = obj.output()(action=url('/form/launch'))

        # here put needed tmplcontexts
        kw['_pp']=json.dumps({'id' : id})
        return {'page' : 'form', 'title' : obj.title(), 'value' : kw}

    @expose()
    def launch(self, _pp, *args, **kw):
        print '[x] LAUNCH _pp , %s, %s, %s' % (_pp, args, kw)
        pp = json.loads(_pp)
        form_id = pp.get('id', False)
        if not form_id:
            raise redirect(url('./error', {"Form id not found" : 'fatal'}))

        plug = plugin.get_plugin_byId(form_id)
        form = plug.plugin_object.output()(action='validation')

        try:
            kw['_pp']=_pp
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            import traceback, sys
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)

            flash(e, 'error')
            raise redirect(url('./index', params={'id' : form_id}, **kw))

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


