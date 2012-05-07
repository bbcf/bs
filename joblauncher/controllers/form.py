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
from joblauncher import handler
from joblauncher.lib.tasks import tasks
from joblauncher.lib import services, io
from joblauncher import lib

__all__ = ['FormController']




to_treat_as_file_list = {'SingleSelectField' : False, 'MultipleSelectField' : True}
"""
Dict to discriminate file list and know if they can be multiple or single.
"""

def parse_parameters(id, fields, **kw):
    """
    Reformat parameters coming to get the form well displayed.
    value are the "normal" parameters and
    childs_args are the ones to get the list of files.
    pp are the private parameters
    """
    value = {}
    child_args = {}
    pp = {}
    save = {}
    for field in fields:
        if field.id is not None:
            key = field.__class__.__name__
            if to_treat_as_file_list.has_key(key):
                _list = json.loads(kw.get(field.id, "[]"))
                child_args[field.id] = {'options' : dict([(_list[i], _list[i]) for i in xrange(len(list(_list)))])}
                save[field.id] = _list
            else :
                value[field.id]=kw.get(field.id, None)
    pp['id'] = id
    pp['save_list'] = save
    return value, child_args, pp

class FormController(BaseController):
    allow_only = has_permission(constants.permissions_read_name)


    @expose('json')
    @expose('joblauncher.templates.form_list')
    def list(self, *args, **kw):
        """
        Method to get the operations list
        """
        operations_path = 'operations_path = %s' % json.dumps(plugin.get_plugins_path(), default=plugin.encode_tree)
        return {'page' : 'form', 'paths' : operations_path}
        paths = plugin.get_plugins_path()

    @expose()
    def error(self, *args, **kw):
        return {'error' : 'bad request : %s ' % kw}



    @expose('joblauncher.templates.plugin_form')
    def index(self, id, *args, **kw):
        """
        Method to get the form
        """
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))

        user = handler.user.get_user_in_session(request)
        if not checker.authorized():
            raise redirect(url('./error', {'not authorized' : id}))

        obj = plug.plugin_object

        form =  obj.output()
        value, child_args, _pp = parse_parameters(id, form.fields, **kw)
        tmpl_context.form = form(action=url('/form/launch'))
        value['_pp'] = json.dumps(_pp)
        return {'page' : 'form', 'title' : obj.title(), 'value' : value, 'ca' : child_args}

    @expose()
    def fire(self, id, *args, **kw):
        """
        Method to call from command-line
        """
        plug = plugin.get_plugin_byId(id)
        user = handler.user.get_user_in_session(request)
        if not checker.authorized():
            raise redirect(url('./error', {'not authorized' : id}))
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))
        kw['_pp']=json.dumps({'id' : id})
        return self.launch(*args, **kw)

    @expose()
    def launch(self, _pp, **kw):
        """
        Launch the tasks
        """
        pp = json.loads(_pp)
        form_id = pp.get('id', False)
        if not form_id:
            raise redirect(url('./error', {"Form id not found" : 'fatal'}))

        plug = plugin.get_plugin_byId(form_id)
        form = plug.plugin_object.output()(action='validation')


        ### VALIDATE ###
        try:
            kw['_pp']=_pp
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            import traceback, sys
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            if pp.has_key('save_list'):
                for k, v in pp['save_list'].iteritems():
                    kw[k] = json.dumps(v)

            if kw.has_key('_pp'): del kw['_pp']
            flash(e, 'error')
            raise redirect(url('./index', params={'id' : form_id}, **kw))

        user = handler.user.get_service_in_session(request)

        ### FETCH FILES ###
        try :
            tmp_dir = services.io.fetch_files(user, pp['save_list'], kw)
        except Exception as e:
            if pp.has_key('save_list'):
                for k, v in pp['save_list'].iteritems():
                    kw[k] = json.dumps(v)
            if kw.has_key('_pp'): del kw['_pp']
            flash(e, 'error')
            raise redirect(url('./index', params={'id' : form_id}, **kw))


        service = constants.decypher_service_name(user.name)
        out_path = services.io.out_path(service)
        callback_url = services.service_manager.get(service, constants.SERVICE_CALLBACK_URL_PARAMETER)

        ### PLUGIN PROCESS ###
        async_res = tasks.plugin_process.delay(form_id, service, tmp_dir, out_path, callback_url, **kw)
        task_id = async_res.task_id
        ### UPDATE DB ###
        handler.database.new_request(kw, task_id, out_path)

        flash('Job launched')
        raise redirect(url('./done',  {'task_id' : task_id}))

    @expose()
    def done(self, *args, **kw):
        return '%s' % ( kw)

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

        return {'page' : 'form', 'info' : info, 'title' : title, 'parameters' : params, 'id' : id}


