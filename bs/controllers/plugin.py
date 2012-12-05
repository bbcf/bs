# -*- coding: utf-8 -*-
import json
import tw2
import tg
import os
from formencode import Invalid
from tg import expose

from bs.lib import base, services, constants, logger, util, filemanager

from bs.operations import util as putil
from bs.operations import wordlist

from bs.celery import tasks
from bs.model import DBSession, PluginRequest, Plugin, Job, Result, Task

import tw2.core as twc


class PluginController(base.BaseController):
    """
    Plugin visual
    """
    @expose('json')
    @logger.identify
    def index(self, ordered=False):
        """
        Get all plugins available
        @param ordered: if you want a nested json based on
        plugins paths
        """
        user = util.get_user(tg.request)
        if user.is_service:
            d = {'plugins': putil.get_plugins_path(service=user, ordered=ordered)}
        else:
            d = {'plugins': putil.get_plugins_path(ordered=ordered)}
        return d

    @expose('mako:bs.templates.plugin_form')
    @logger.identify
    @logger.log_connection
    def get(self, id, *args, **kw):
        """
        Display the form by it's id
        """
        # check plugin id
        plug = None
        try:
            plug = putil.get_plugin_byId(id)
        except:
            tg.abort(400, "Bad plugin identifier")

        # get the plugin
        obj = plug
        info = obj.info
        form = info.get('output')
        desc = info.get('description')

        # parse request parameters
        prefill_fields(info.get('in'), form, **kw)
        #value = parse_parameters(user, id, form, info.get('in'), **kw)
        value = {}

        # private parameters from BioScript application to pass to the form
        pp = {'id': id}
        value = {'pp': json.dumps(pp)}

        # prepare form output
        main_proxy = tg.config.get('main.proxy')
        widget = form(action=main_proxy + tg.url('/plugins/validate', {'id': id})).req()
        widget.value = value

        return {'page': 'plugin', 'desc': desc, 'title': info.get('title'), 'widget': widget}

    @expose()
    @logger.identify
    @logger.log_connection
    def validate(self, **kw):
        """
        plugin parameters validation
        """
        user = util.get_user(tg.request)

        # check parameters
        pp = kw.get('pp', None)
        if pp is None:
            tg.abort(400, "Plugin identifier not found in the request.")

        pp = json.loads(pp)
        plugin_id = pp.get('id', None)
        if plugin_id is None:
            tg.abort(400, "Plugin identifier not found in the request.")

        # check plugin id
        plug = putil.get_plugin_byId(plugin_id)
        if plug is None:
            tg.abort(400, "Bad plugin identifier")

        # get plugin form output
        obj = plug
        info = obj.info
        form = info.get('output')(action='validation')

        # callback
        callback = kw.get('callback', 'callback')
        # get the plugin from the database
        plugin_db = DBSession.query(Plugin).filter(Plugin.generated_id == obj.unique_id()).first()
        plugin_request = _log_form_request(plugin_id=plugin_db.id, user=user, parameters=kw)

        try:
            form.validate(kw)
        except (tw2.core.ValidationError, Invalid) as e:
            main_proxy = tg.config.get('main.proxy')
            e.widget.action = main_proxy + tg.url('plugins/index', {'id': plugin_id})
            modified = prefill_fields(info.get('in'), form, **kw)
            pp = {'id': plugin_id, 'modified': json.dumps(modified)}
            value = {'pp': json.dumps(pp)}

            e.widget.value = value

            plugin_request.status = 'FAILED'
            plugin_request.error = str(e)
            DBSession.add(plugin_request)
            return jsonp_response(**{'validation': 'failed', 'desc': info.get('description'),
                    'title': info.get('title'), 'widget': e.widget.display(), 'callback': callback})
        try:
            inputs_directory = filemanager.fetch(user, obj, kw)
        except Exception as e:
            plugin_request.status = 'FAILED'
            plugin_request.error = str(e)
            DBSession.add(plugin_request)
            import sys
            import traceback
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            return jsonp_response(**{'validation': 'success', 'desc': info.get('description'),
                                    'title':  info.get('title'), 'error': 'error while fetching files : ' + str(e), 'callback': callback})

        # get output directory to write results
        outputs_directory = filemanager.temporary_directory()
        service_callback = None
        if user.is_service:
            outputs_directory = services.io.out_path(user.name)
            service_callback = services.service_manager.get(user.name, constants.SERVICE_CALLBACK_URL_PARAMETER)

        # call plugin process
        user_parameters = kw.get('_up', None)
        if user_parameters:
            user_parameters = json.loads(user_parameters)

        bioscript_callback = tg.config.get('main.proxy') + '/' + tg.url('plugins/callback_results')

        plugin_info = {'title': info['title'],
                        'plugin_id': plugin_db.id,
                        'generated_id': plugin_db.generated_id,
                        'description': info['description'],
                        'path': info['path'],
                        'in': info['in'],
                        'out': info['out'],
                        'meta': info['meta']}

        async_res = tasks.plugin_job.delay(user.name, inputs_directory, outputs_directory, plugin_info,
            user_parameters, service_callback, bioscript_callback, **kw)
        task_id = async_res.task_id
        _log_job_request(plugin_request.id, task_id)
        return jsonp_response(**{'validation': 'success', 'plugin_id': plugin_id, 'task_id': task_id, 'callback': callback})

    @expose('json')
    def callback_results(self, task_id, results):
        results = json.loads(results)
        for result in results:
            task = DBSession.query(Task).filter(Task.task_id == task_id).first()
            res = Result()
            res.job_id = task.job.id
            if result.get('is_file', False):
                res.is_file = True
                res.path = result.get('path')
                res._type = result.get('type')
                res.fname = os.path.split(res.path)[1]
            else:
                res.result = result.get('value')
            DBSession.add(res)
        return {'status': 'success', 'retval': 1}


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
    if 'prefill' in kw:
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
                        #TODO utility method to get all children
                        for field in form.children_deep():
                            if field.id == fid:
                                if multiple:
                                    mod = _change_file_field(form, field, tw2.forms.MultipleSelectField, prefill_with)
                                else:
                                    mod = _change_file_field(form, field, tw2.forms.SingleSelectField, prefill_with)
                                modified.append(mod)
        return modified


def _change_file_field(form, field, cls, value):
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
        else:
            tmp.options = dict([(value[i], value[i]) for i in xrange(len(list(value)))])
    else:
        tmp.options = []
    # replace

    tmp_parent = field.parent
    parent_deep = 1
    tmp_form = form
    while(tmp_parent != form):
        tmp_parent = tmp_parent.parent
        parent_deep += 1
        tmp_form = tmp_form.child
    for index, f in enumerate(tmp_form.children):
        if f.id == field.id:
            tmp_form.children[index] = tmp
    return field.id


def jsonp_response(**kw):
    # encode in JSONP here cauz there is a problem with custom renderer
    tg.response.headers['Content-Type'] = 'text/javascript'
    return '%s(%s)' % (kw.get('callback', 'callback'), tg.json_encode(kw))


def _log_form_request(plugin_id, user, parameters):
    """
    log the plugin form submission.
    """
    pl = PluginRequest()
    pl.plugin_id = plugin_id
    pl.user = user
    pl.parameters = get_formparameters(parameters)
    DBSession.add(pl)
    DBSession.flush()
    return pl

PRIVATE_BS_PARAMS = ['pp', 'up', 'callback', 'key']


def get_formparameters(params):
    d = {}
    for k, v in params.iteritems():
        if k not in PRIVATE_BS_PARAMS:
            if not isinstance(v, basestring):
                value = v.filename
            elif not isinstance(v, list, set):
                value = str(v)
            else:
                value = v
            d[k] = value
    return d


def _log_job_request(request_id, task_id):
    job = Job()
    job.request_id = request_id
    job.task_id = task_id
    DBSession.add(job)
    return job
