# -*- coding: utf-8 -*-
import json, tw2, tg
from formencode import Invalid
from tg import expose

from bs.lib import base, util, services, constants
from bs.lib.services import service_manager

from bs.operations import util as putil
from bs.operations import wordlist
from bs.operations.base import MultipleFileUpload

from bs.celery import tasks

from bs import handler

import tw2.core as twc







class PluginController(base.BaseController):
    """
    Plugin visual
    """
    @expose('json')
    def index(self, ordered=False):
        """
        Get all plugins available
        @param ordered: if you want a nested json based on
        plugins paths
        """
        user = handler.user.get_user_in_session(tg.request)
        if user.is_service :
            d = {'plugins' : putil.get_plugins_path(service=user, ordered=ordered)}
        else :
            d = {'plugins' : putil.get_plugins_path(ordered=ordered)}
        return d


    @expose('mako:bs.templates.plugin_form')
    def get(self, id, *args, **kw):
        print 'get'
        print kw
        """
        Display the form by it's id
        """
        # check plugin id
        plug = putil.get_plugin_byId(id)
        if plug is None:
            tg.abort(400, "Bad plugin identifier")

        # get the plugin
        obj = plug.plugin_object
        info = obj.info
        form =  info.get('output')
        desc = info.get('description')

        # parse request parameters
        modified = prefill_fields(info.get('in'), form, **kw)

        #value = parse_parameters(user, id, form, info.get('in'), **kw)
        value = {}

        # private parameters from BioScript application to pass to the form
        pp = {'id' : id, 'modified' : json.dumps(modified)}
        value = { 'pp' : json.dumps(pp)}



        # prepare form output
        main_proxy = tg.config.get('main.proxy')
        widget = form(action= main_proxy + tg.url('/plugin/validate', {'id' : id})).req()
        widget.value = value

        return {'page' : 'plugin', 'desc' : desc, 'title' : info.get('title'), 'widget' : widget}



    @expose()
    def validate(self, **kw):
        """
        plugin parameters validation
        """
        user = handler.user.get_user_in_session(tg.request)

        util.debug("PLUGIN SUBMITTED")

        # check parameters
        pp = kw.get('pp', None)
        if pp is None:
            tg.abort(400, "Plugin identifier not found in the request.")

        pp = json.loads(pp)
        form_id = pp.get('id', None)
        if form_id is None:
            tg.abort(400, "Plugin identifier not found in the request.")

        # check plugin id
        plug = putil.get_plugin_byId(form_id)
        if plug is None:
            tg.abort(400, "Bad plugin identifier")

        # get plugin form output
        obj = plug.plugin_object
        info = obj.info
        form = info.get('output')(action='validation')

        # validate
        util.debug("VALIDATE")

        # callback
        callback = kw.get('callback', 'callback')

        try:
            form.validate(kw)
        except (tw2.core.ValidationError ,Invalid) as e:
            main_proxy = tg.config.get('main.proxy')
            e.widget.action = main_proxy + tg.url('plugins/index', {'id' : form_id})
            modified = prefill_fields(info.get('in'), form, **kw)
            pp = {'id' : form_id, 'modified' : json.dumps(modified)}
            value = { 'pp' : json.dumps(pp)}

            e.widget.value = value
            util.debug("VALIDATION FAILED " + str(e))
#            import sys, traceback
#            etype, value, tb = sys.exc_info()
#            traceback.print_exception(etype, value, tb)
            return jsonp_response(**{'validation':'failed', 'desc' : info.get('description'),
                    'title' :  info.get('title'), 'widget' : e.widget.display(), 'callback' : callback})


        util.debug("VALIDATION PASSED")
        # fetch files if any
        try :
            _fs = [p.get('id') for p in obj.in_params_typeof(wordlist.FILE)]
            modified = json.loads(pp.get('modified'))
            
            tmp_dir = services.io.fetch(user, _fs, kw)

        except Exception as e:
            import sys, traceback
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            return jsonp_response(**{'validation':'success', 'desc' : info.get('description'),
                                    'title' :  info.get('title'), 'error' : e.read(), 'callback' : callback})

        # get output directory to write results
        service = user.name
        if user.is_service :
            out_path = services.io.out_path(service)
            callback_url = services.service_manager.get(service, constants.SERVICE_CALLBACK_URL_PARAMETER)
        else:
            out_path = service_manager.out_path
            callback_url = None

        # call plugin process
        async_res = tasks.plugin_process.delay(form_id, service, tmp_dir, out_path, info.get('title'),
            info.get('description'), callback_url, **kw)

        task_id = async_res.task_id

        # update database information
        handler.database.new_request(kw, task_id, out_path)
        return jsonp_response(**{'validation': 'success', 'form_id' : form_id, 'task_id' : task_id, 'callback' : callback})




def prefill_fields(form_parameters, form, **kw):
    """
    If prefill key is in the request,
    we must pre-fill some fields and perhaps change their definition
    :param form_parameters: the 'in' parameters of the form
    :param form: the 'form widget'
    :param kw: the parameters in the request
    :return:
    """

    modified = []   # list of modified fields
    if kw.has_key('prefill'):
        prefill = json.loads(kw.get('prefill'))
        for type_to_prefill, prefill_with in prefill.iteritems():
            for fparam in form_parameters:
                # check which "type" to prefill
                if wordlist.is_of_type(fparam.get('type'), type_to_prefill):
                    fid = fparam.get('id')
                    kw[fid] = prefill_with
                    # if fparam is of `file` type, we need to modify it
                    if wordlist.is_of_type(fparam.get('type'), wordlist.FILE):
                        multiple = fparam.get('multiple', False)
                        for index, field in enumerate(form.children):
                            if field.id == fid:
                                if multiple     : mod = _change_file_field(form, field, tw2.forms.MultipleSelectField, index, prefill_with)
                                else            : mod = _change_file_field(form, field, tw2.forms.SingleSelectField, index, prefill_with)
                                modified.append(mod)
    return modified

def _change_file_field(form, field, cls, index, value):
    """
    Modify field type
    :param form: the 'form widget'
    :param field: the field to modify
    :param cls: the cls to replace the field with
    :param index: the position of the field in the form
    :param value: fill the new field with "value"
    """

    # prepare
    tmp = cls()
    tmp.id = field.id
    if field.validator is not None:
        tmp.validator = twc.Validator(required=True)
    tmp.name = field.name
    # fill
    if len(value) > 0:
        if isinstance(value[0], (list, tuple)):
            tmp.options = [(value[i][0], value[i][1]) for i in xrange(len(list(value)))]
        else :
            tmp.options = dict([(value[i], value[i]) for i in xrange(len(list(value)))])
    else :
        tmp.options=[]
    # replace
    form.children[index] = tmp
    return field.id

def jsonp_response(**kw):
    # encode in JSONP here cauz there is a problem with custom renderer
    tg.response.headers['Content-Type'] = 'text/javascript'
    return '%s(%s)' % (kw.get('callback', 'callback'), tg.json_encode(kw))

#    @expose('mako:bs.templates.fupload')
#    def fupload(self):
#        return {}
#
#    @expose('bs.templates.after_submission_hook')
#    def after_submit_hook(self, task_id, form_id):
#        user = handler.user.get_user_in_session(request)
#        return {'task_id' : task_id, 'form_id' : form_id , 'bs_redirect' : url('./submitted')}
#
#    @expose('bs.templates.submitted')
#    def submitted(self, task_id):
#        requesturl = url("/requests")
#        lresult = requesturl + "/result?task_id=" + task_id
#        lstatus = requesturl + "/status?task_id=" + task_id
#        return {'page' : 'submitted', 'lresult' : lresult, 'lstatus' : lstatus}
#
#    @expose()
#    def done(self, *args, **kw):
#        return '%s' % ( kw)
#
#    @expose('json')
#    @expose('bs.templates.form_info')
#    def info(self, id):
#        plug = plugin.get_plugin_byId(id)
#        if plug is None:
#            raise redirect(url('./error', {'bad form id' : id}))
#        o = plug.plugin_object
#        info = o.description()
#        title = o.title()
#        params = o.parameters()
#
#        return {'page' : 'form', 'info' : info, 'title' : title, 'parameters' : params, 'id' : id}
#
#
#def parse_parameters(user, id, form, in_params, **kw):
#    """
#    Reformat parameters to get the form well displayed depending
#    of the service.
#    - check if the form is pre-filled by a service
#    - replace select fields by file upload field if there is no service or service did not pre-fill
#    """
#    fields = form.child.children
#    # check if the form is pre-filled by type
#    if kw.has_key('prefill'):
#        prefill = json.loads(kw.get('prefill'))
#        for t, l in prefill.iteritems():
#            for param in in_params:
#                if wordlist.is_of_type(param.get('type'), t):
#                    kw[param.get('id')] = l
#
#                    # map field id to boolean multiple if file is `file` type
#                #    d = dict( [(param.get('id'), param.get('multiple', False)) for param in in_params if wordlist.is_of_type(param.get('type'), wordlist.FILE)])
#                #    # change field if it's multiple or simple only if it's a `file` field
#                #    for index, field in enumerate(fields):
#                #        fid = field.id
#                #        if d.has_key(fid):
#                #            if d.get(fid) : _process_file_field(user, form, field, kw, plugin.MultipleFileUpload, index, False)
#                #            else          : _process_file_field(user, form, field, kw, tw2.forms.FileField, index, True)
#
#
#    # add form private parameters
#    pp = {}
#    pp['id']=id
#    kw['pp']=json.dumps(pp)
#    return kw
#

#
#
#
#
#def _process_file_field(user, form, field, params, cls, index, take_validator):
#    """
#    Process the file field (fill it or change it)
#    """
#    if user.is_service and  params.has_key(field.id): # fill fields
#        _fill_fields(field, field.id, params)
#    else : # replace field for direct user input
#        if take_validator: tmp = cls(validator=tw2.forms.FileValidator(required=True))
#        else :             tmp = cls()
#        tmp.id = field.id
#        tmp.label = field.label
#        form.child.children[index] = tmp
#
#
#
#
