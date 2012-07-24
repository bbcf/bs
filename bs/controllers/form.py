# -*- coding: utf-8 -*-
from tg import request, expose, url, flash, response, require
from tg.controllers import redirect
from bs.lib.base import BaseController
from bs.lib import constants, checker
from bs.lib.plugins import plugin
from bs import handler
from repoze.what.predicates import has_permission
import json
from pylons import tmpl_context

from bs import handler
from bs.lib.tasks import tasks
from bs.lib import services, io
from bs.lib.services import service_manager
from bs import lib
import tg
from formencode import Invalid
from paste.request import get_cookies
__all__ = ['FormController']
import tw2.forms
import tw2.core
import tw2.dynforms
from webob import Request

from paste.auth import auth_tkt

"""
Dict to discriminate file list and know if they can be multiple or single.
"""

def parse_parameters(user, id, form, files, **kw):
    """
    Reformat parameters coming to get the form well displayed.
    value are the "normal" parameters and
    childs_args are the ones to get the list of files.
    pp are the private parameters
    """
    # fill list param
    fields = form.child.children
    if isinstance(files, (list, tuple)):
        simples = files
        multiples = []
    else :
        simples = files.get('simple', [])
        multiples = files.get('multiple', [])

    for index, field in enumerate(fields):
        fid = field.id
        if fid in simples:
            _process_file_field(user, form, field, kw, tw2.forms.FileField, index, True)
        elif fid in multiples:
            _process_file_field(user, form, field, kw, plugin.MultipleFileUpload, index, False)


#    value = {}
#    for k, v in kw.iteritems():
#        value[k]=v
#
#    # edit private parameters
#    if kw.has_key('key'):
#        value['key']=kw.get('key')
#    if kw.has_key('up'):
#        value['up']=kw.get('up')

    pp = {}
    pp['id']=id
    kw['pp']=json.dumps(pp)


    return kw

def _fill_fields(field, field_id, params):
    _list = json.loads(params.get(field_id, "[]"))
    if len(_list)>0:
        if isinstance(_list[0], (list, tuple)):
            field.options = [(_list[i][0], _list[i][1]) for i in xrange(len(list(_list)))]
        else :
            field.options = dict([(_list[i], _list[i]) for i in xrange(len(list(_list)))])
    else :
        field.options=[]




def _process_file_field(user, form, field, params, cls, index, take_validator):
    if user.is_service: # fill fields
        _fill_fields(field, field.id, params)
    else : # replace field for direct user input
        if take_validator: tmp = cls(validator=field.validator)
        else :             tmp = cls()
        tmp.id = field.id
        tmp.label = field.label
        form.child.children[index] = tmp

def _format_submission_parameters(files, params):
    pass

def _format_submission_parameters2(files, params):
    if files.has_key('multiple'):
        for m in files.get('multiple'):
            mlist = []
            todel = []
            for k, v in params.iteritems():
                if k.startswith(m) and len(k.split(':')) == 3:
                    p, n, f = k.split(':')
                    if p == m and f == 'file':
                        if v != '':
                            mlist.append(v)
                        todel.append(k)
            for d in todel: del params[d]
            params[m] = mlist

class FormController(BaseController):

    @expose('json')
    @expose('bs.templates.form_list')
    def list(self, *args, **kw):
        """
        Method to get the operations list
        """
        operations_path = 'operations_path = %s' % json.dumps(plugin.get_plugins_path(), default=plugin.encode_tree)
        return {'page' : 'form', 'paths' : operations_path}


    @expose('json')
    def methods(self, **kw):
        user = handler.user.get_user_in_session(request)
        return {'paths' : json.dumps(plugin.get_plugins_path(service=user), default=plugin.encode_tree)}

    @expose()
    def error(self, *args, **kw):
        return {'error' : 'bad request : %s ' % kw}




    @expose('bs.templates.plugin_form')
    def index(self, id, *args, **kw):
        """
        Method to get the form
        """
        # SERVICE DEFINED
        if request.method == 'GET':
        # get the plugin
            plug = plugin.get_plugin_byId(id)
            if plug is None:
                raise redirect(url('./error', {'bad form id' : id}))

            obj = plug.plugin_object
            form =  obj.output()
            info = obj.description()
            user = handler.user.get_user_in_session(request)
            value = parse_parameters(user, id, form, obj.files(), **kw)

            main_proxy = tg.config.get('main.proxy')

            widget = form(action= main_proxy + url('/form/index', {'id' : id})).req()
            widget.value = value
            return {'page' : 'form', 'info' : info, 'title' : obj.title(), 'widget' : widget}

        else :
            # FORM SUBMITTED
            pp = kw.get('pp', None)
            if pp is None:
                flash('Form id not found.', 'error')
                raise redirect(url('/'))

            pp = json.loads(pp)
            form_id = pp.get('id', None)
            if form_id is None:
                flash('Form id not found.', 'error')
                raise redirect(url('/'))

            up = kw.get('up', None)
            if up is None:
                flash('Bad form ("up" parameter is missing)', 'error')
                raise redirect(url('/'))

            key = kw.get('key', None)
            if up is None:
                flash('Bad form ("key" parameter is missing).', 'error')
                raise redirect(url('/'))


            plug = plugin.get_plugin_byId(form_id)
            if plug is None:
                flash('Form id %s not found.' % form_id, 'error')
                raise redirect(url('/'))

            form = plug.plugin_object.output()(action='validation')
            info = plug.plugin_object.description()

            ### VALIDATE ###
            try:
                form.validate(kw)
            except (tw2.core.ValidationError ,Invalid) as e:
                main_proxy = tg.config.get('main.proxy')
                e.widget.action = main_proxy + url('/form/index', {'id' : id})
                return {'page' : 'form', 'info' : info, 'title' :  plug.plugin_object.title(), 'widget' : e.widget}

            user = handler.user.get_service_in_session(request)

            ### FETCH FILES ###
            try :
                if user.is_service :
                    tmp_dir = services.io.fetch_files(user, plug.plugin_object.files(), kw)
                else :
                    tmp_dir = services.io.fetch_file_field(user, plug.plugin_object.files(), kw)

            except Exception as e:
                flash(e, 'error')
                import sys, traceback
                etype, value, tb = sys.exc_info()
                traceback.print_exception(etype, value, tb)
                raise redirect(url('./index', params={'id' : form_id}))

            service = user.name
            if user.is_service :
                out_path = services.io.out_path(service)
                callback_url = services.service_manager.get(service, constants.SERVICE_CALLBACK_URL_PARAMETER)
            else:
                out_path = service_manager.out_path
                callback_url = None

            ### PLUGIN PROCESS ###
            async_res = tasks.plugin_process.delay(form_id, service, tmp_dir, out_path, plug.plugin_object.title(), plug.plugin_object.description(), callback_url, **kw)

            task_id = async_res.task_id
            ### UPDATE DB ###
            handler.database.new_request(kw, task_id, out_path)

            flash('Job launched with id %s' % task_id)
            raise redirect(url('./submitted',  params={'task_id' : task_id}))

    @expose('bs.templates.submitted')
    def submitted(self, task_id):
        requesturl = url("/requests")
        lresult = requesturl + "/result?task_id=" + task_id
        lstatus = requesturl + "/status?task_id=" + task_id

        return {'page' : 'submitted', 'lresult' : lresult, 'lstatus' : lstatus}
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
    def launch(self, **kw):
        """
        Launch the tasks
        """
        t = {'up': u'', 'pp': u'{"id": "e2f47e2950eeba6aff70ee70ca8923cc7eefc01f"}', 'two': u'', 'key': u'', 'one': u'7'}
        print kw


        raise redirect(url('./index', params={'id' : form_id}))



    @expose()
    def done(self, *args, **kw):
        return '%s' % ( kw)

    @expose('json')
    @expose('bs.templates.form_info')
    def info(self, id):
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))
        o = plug.plugin_object
        info = o.description()
        title = o.title()
        params = o.parameters()

        return {'page' : 'form', 'info' : info, 'title' : title, 'parameters' : params, 'id' : id}


