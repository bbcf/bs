# -*- coding: utf-8 -*-
from tg import request, expose, url, flash, response, require
from tg.controllers import redirect
from bs.lib.base import BaseController
from bs.lib import constants, checker, util
from bs.lib.plugins import plugin, wordlist
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

def parse_parameters(user, id, form, in_params, **kw):
    """
    Reformat parameters to get the form well displayed depending
    of the service.
    - check if the form is pre-filled by a service
    - replace select fields by file upload field if there is no service or service did not pre-fill
    """
    fields = form.child.children
    # check if the form is pre-filled by type
    if kw.has_key('prefill'):
        prefill = json.loads(kw.get('prefill'))
        for t, l in prefill.iteritems():
            for param in in_params:
                if wordlist.is_of_type(param.get('type'), t):
                    kw[param.get('id')] = l

    # map field id to boolean multiple if file is `file` type
    d = dict( [(param.get('id'), param.get('multiple', False)) for param in in_params if wordlist.is_of_type(param.get('type'), wordlist.FILE)])
    # change field if it's multiple or simple only if it's a `file` field
    for index, field in enumerate(fields):
        fid = field.id
        if d.has_key(fid):
            if d.get(fid) : _process_file_field(user, form, field, kw, plugin.MultipleFileUpload, index, False)
            else          : _process_file_field(user, form, field, kw, tw2.forms.FileField, index, True)


    # add form private parameters
    pp = {}
    pp['id']=id
    kw['pp']=json.dumps(pp)
    return kw

def _fill_fields(field, field_id, params):
    """
    Fill field options with pre-filled values
    """
    _list = params.get(field_id, "[]")
    if len(_list)>0:
        if isinstance(_list[0], (list, tuple)):
            field.options = [(_list[i][0], _list[i][1]) for i in xrange(len(list(_list)))]
        else :
            field.options = dict([(_list[i], _list[i]) for i in xrange(len(list(_list)))])
    else :
        field.options=[]




def _process_file_field(user, form, field, params, cls, index, take_validator):
    """
    Process the file field (fill it or change it)
    """
    if user.is_service and  params.has_key(field.id): # fill fields
        _fill_fields(field, field.id, params)
    else : # replace field for direct user input
        if take_validator: tmp = cls(validator=tw2.forms.FileValidator(required=True))
        else :             tmp = cls()
        tmp.id = field.id
        tmp.label = field.label
        form.child.children[index] = tmp


class FormController(BaseController):



   # @expose('mako:bs.templates.plugin_form')
    @expose('jsonp:')
    def index(self, id, *args, **kw):
        """
        Method to get the form
        """
        return {'bluou' : 'bjhb'}
        user = handler.user.get_user_in_session(request)

        # Display form
        if not kw.has_key('pp'):
            # get the plugin
            plug = plugin.get_plugin_byId(id)
            if plug is None:
                raise redirect(url('./error', {'bad form id' : id}))

            obj = plug.plugin_object
            info = obj.info
            form =  info.get('output')
            desc = info.get('description')

            value = parse_parameters(user, id, form, info.get('in'), **kw)

            main_proxy = tg.config.get('main.proxy')

            widget = form(action= main_proxy + url('/form/index', {'id' : id})).req()
            widget.value = value
            return {'page' : 'form', 'desc' : desc, 'title' : info.get('title'), 'widget' : widget}

        else :
            util.debug("FORM SUBMITTED")
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

            obj = plug.plugin_object
            info = obj.info
            form = info.get('output')(action='validation')
            #value = parse_parameters(user, id, form, info.get('in'), **kw)
            util.debug("VALIDATE %s" % kw)
            ### VALIDATE ###
            try:
                form.validate(kw)
            except (tw2.core.ValidationError ,Invalid) as e:
                main_proxy = tg.config.get('main.proxy')
                e.widget.action = main_proxy + url('/form/index', {'id' : id})
                return {'page' : 'form', 'desc' : info.get('description'), 'title' :  info.get('title'), 'widget' : e.widget}

            user = handler.user.get_service_in_session(request)
            util.debug("VALIDATION PASSED")
            ### FETCH FILES ###
            try :
                _fs = [p.get('id') for p in obj.in_params_typeof(wordlist.FILE)]
                if user.is_service :
                    tmp_dir = services.io.fetch_files(user, _fs, kw)
                else :
                    tmp_dir = services.io.fetch_file_field(user, _fs, kw)

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
            async_res = tasks.plugin_process.delay(form_id, service, tmp_dir, out_path, info.get('title'), info.get('description'), callback_url, **kw)

            task_id = async_res.task_id
            ### UPDATE DB ###
            handler.database.new_request(kw, task_id, out_path)

            flash('Job launched with id %s' % task_id)
            raise redirect(url('./after_submit_hook',  params={'form_id' : form_id, 'task_id' : task_id}))

    @expose('bs.templates.after_submission_hook')
    def after_submit_hook(self, task_id, form_id):
        user = handler.user.get_user_in_session(request)
        return {'task_id' : task_id, 'form_id' : form_id , 'bs_redirect' : url('./submitted')}

    @expose('bs.templates.submitted')
    def submitted(self, task_id):
        requesturl = url("/requests")
        lresult = requesturl + "/result?task_id=" + task_id
        lstatus = requesturl + "/status?task_id=" + task_id
        return {'page' : 'submitted', 'lresult' : lresult, 'lstatus' : lstatus}

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


