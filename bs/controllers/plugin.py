# -*- coding: utf-8 -*-
import json
import tw2
import tg
import os
from formencode import Invalid
from tg import expose, response
import copy

from bs.lib import base, services, constants, logger, util, filemanager

from bs.operations import util as putil
from bs.operations import wordlist

from bs.celery import tasks
from bs.model import DBSession, PluginRequest, Plugin, Job, Result, Task

import tw2.core as twc

DEBUG_LEVEL = 0


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[plugin controller] %s%s' % ('\t' * t, s)


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
    def fetch(self, oid, *args, **kw):
        """
        Display the form by it's id
        """
        # check plugin id
        plug = None
        try:
            plug = putil.get_plugin_byId(oid)
        except:
            tg.abort(400, "Bad plugin identifier")

        debug('get plugin %s' % oid)
        # get the plugin
        obj = plug
        info = obj.info
        form = info.get('output')()
        desc = info.get('description')
        debug('params =  %s' % kw, 1)
        # bioscript parameters
        bs_private = {}
        if 'bs_private' in kw:
            bs_private = json.loads(kw['bs_private'])
            debug("get bs private parameters %s" % bs_private, 2)

        if 'prefill' in bs_private:
            prefill_fields(info.get('in'), form, bs_private['prefill'], kw)

        # {'bs_private': {'app': pp, 'cfg': handler.job.bioscript_config, 'prefill': prefill}})

        # add some private parameters from BioScript
        pp = {'id': oid}
        # if user is a serviec, add the key & the mail in the authentication
        user = util.get_user(tg.request)
        if user.is_service:
            pp['mail'] = user.email
            pp['key'] = user.key
        bs_private['pp'] = pp

        # prepare form output
        main_proxy = tg.config.get('main.proxy')
        widget = form(action=main_proxy + tg.url('/plugins/validate', {'id': oid})).req()
        widget.value = {'bs_private': json.dumps(bs_private), 'key': user.key}
        debug('display plugin with bs_private : %s' % bs_private)
        debug('vaaalue : %s' % widget.value)

        debug(user)
        return {'page': 'plugin', 'desc': desc, 'title': info.get('title'), 'widget': widget}

    @expose()
    @logger.identify
    @logger.log_connection
    def validate(self, **kw):
        """
        plugin parameters validation
        """
        user = util.get_user(tg.request)
        debug('Got request validation from user %s' % user)
        if not 'bs_private' in kw:
            tg.abort(400, "Plugin identifier not found in the request.")
        debug('params %s' % kw, 1)

        bs_private = copy.deepcopy(json.loads(kw['bs_private']))
        debug('private %s' % bs_private, 1)
        plugin_id = bs_private['pp']['id']
        if plugin_id is None:
            tg.abort(400, "Plugin identifier not found in the request.")

        # check plugin id
        plug = putil.get_plugin_byId(plugin_id)
        if plug is None:
            tg.abort(400, "Bad plugin identifier")

        # get plugin form output
        obj = plug
        info = obj.info
        form = info.get('output')()

        # callback for jsonP
        callback = kw.get('callback', 'callback')
        # get the plugin from the database
        plugin_db = DBSession.query(Plugin).filter(Plugin.generated_id == obj.unique_id()).first()
        plugin_request = _log_form_request(plugin_id=plugin_db.id, user=user, parameters=kw)

        if 'prefill' in bs_private:
            prefill_fields(info.get('in'), form, bs_private['prefill'], kw, replace_value=False)
            debug('prefill in validation', 3)
            del bs_private['prefill']

        response.headerlist.append(('Access-Control-Allow-Origin', '*'))

        # validation
        try:
            debug('Validating parameters %s' % kw, 1)
            # form = form().req()
            form.validate(kw)
        except (tw2.core.ValidationError, Invalid) as e:
            main_proxy = tg.config.get('main.proxy')
            e.widget.action = main_proxy + tg.url('plugins/index', {'id': plugin_id})
            debug('private after validation failed %s' % bs_private, 1)
            #value = {'bs_private': json.dumps(bs_private)}
            #debug('value %s' % value)
            #e.widget.value = value
            plugin_request.status = 'FAILED'
            plugin_request.error = str(e)
            DBSession.add(plugin_request)
            return json.dumps({'validation': 'failed', 'desc': info.get('description'),
                    'title': info.get('title'), 'widget': e.widget.display(), 'callback': callback})
            # return jsonp_response(**{'validation': 'failed', 'desc': info.get('description'),
            #         'title': info.get('title'), 'widget': e.widget.display(), 'callback': callback})
        debug('Validation pass')
        #if the validation passes, remove private parameters from the request
        del kw['bs_private']
        if 'key' in kw:
            del kw['key']
        # fetch form files
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
            return json.dumps({'validation': 'success', 'desc': info.get('description'),
                                    'title':  info.get('title'), 'error': 'error while fetching files : ' + str(e), 'callback': callback})
        debug('Files fetched')
        # get output directory to write results
        outputs_directory = filemanager.temporary_directory(constants.paths['data'])
        service_callback = None
        debug(user)
        if user.is_service:
            debug('is service', 1)
            # def out_path(service_name):
            o = services.service_manager.get(user.name, constants.SERVICE_RESULT_ROOT_PARAMETER)
            if o:
                outputs_directory = o
            service_callback = services.service_manager.get(user.name, constants.SERVICE_CALLBACK_URL_PARAMETER)

        debug('Output dir = %s' % outputs_directory)
        # get user parameters from the request
        user_parameters = bs_private.get('app', "{}")
        debug('get user parameters : %s' % user_parameters, 1)
        # get response config from the request
        resp_config = bs_private.get('cfg', None)

        plugin_info = {'title': info['title'],
                        'plugin_id': plugin_db.id,
                        'generated_id': plugin_db.generated_id,
                        'description': info['description'],
                        'path': info['path'],
                        'in': info['in'],
                        'out': info['out'],
                        'meta': info['meta']}

        # call plugin process
        bioscript_callback = tg.config.get('main.proxy') + '/' + tg.url('plugins/callback_results')
        async_res = tasks.plugin_job.delay(user.name, inputs_directory, outputs_directory, plugin_info,
            user_parameters, service_callback, bioscript_callback, **kw)
        task_id = async_res.task_id

        _log_job_request(plugin_request.id, task_id)

        if resp_config and resp_config.get('plugin_info', '') == 'min':
            return jsonp_response(**{'validation': 'success', 'plugin_id': plugin_id, 'task_id': task_id, 'callback': callback, 'app': user_parameters})
        return json.dumps({
                'validation': 'success',
                'plugin_id': plugin_id,
                'task_id': task_id,
                'plugin_info': json.dumps(
                    {'title': info['title'],
                    'description': info['description'],
                    'path': info['path'],
                    'in': info['in'],
                    'out': info['out'],
                    'meta': info['meta']}),
                'callback': callback, 'app': user_parameters})

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


def prefill_fields(form_parameters, form, prefill_params, kw, replace_value=True):
    """
    If prefill key is in the request,
    we must pre-fill some fields and perhaps change their definition
    :param form_parameters: the 'in' parameters of the form
    :param form: the 'form widget'
    :param kw: the parameters in the request
    :return:
    """

    modified = []   # list of modified fields
    prefill = json.loads(prefill_params)
    debug('PREFILL %s' % prefill_params)
    for type_to_prefill, prefill_with in prefill.iteritems():
        debug('Trying type %s' % type_to_prefill, 1)
        for fparam in form_parameters:
            debug('Trying on parameter %s' % fparam, 2)
            # check which "type" to prefill
            if wordlist.is_of_type(fparam.get('type'), type_to_prefill):
                debug('%s is of type %s' % (type_to_prefill, fparam.get('type')))
                fid = fparam.get('id')
                if replace_value:
                    kw[fid] = prefill_with
                # if fparam is of `file` type, we need to modify it
                if wordlist.is_of_type(fparam.get('type'), wordlist.FILE):
                    debug('CHANGE FILEFIELD ##############################################')
                    multiple = fparam.get('multiple', False)
                    #TODO utility method to get all children
                    for field in form.children_deep():
                        if field.id == fid or fid.startswith('%s:' % field.id):
                            debug('XXXXXXXXXXXXXXXXXXX', 1)
                            if multiple:
                                mod = _change_file_field(form, field, tw2.forms.MultipleSelectField, prefill_with)
                            else:
                                mod = _change_file_field(form, field, tw2.forms.SingleSelectField, prefill_with)
                            modified.append(mod)
        return modified


def _change_file_field(form, field, clazz, value):
    """
    Modify field type
    :param form: the 'form widget'
    :param field: the field to modify
    :param clazz: the clazz to replace the field with
    :param index: the position of the field in the form
    :param value: fill the new field with "value"
    """

    # prepare
    tmp = clazz()
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
    #print 'replace %s with %s' % (field, clazz)
    tmp_parent = field.parent
    parent_deep = 1
    tmp_form = form
    #print tmp_parent
    while(tmp_parent != form):
        tmp_parent = tmp_parent.parent
        #print tmp_parent
        parent_deep += 1
        tmp_form = tmp_form.child
    for index, f in enumerate(tmp_form.children):
        if f.id == field.id:
            tmp_form.children[index] = tmp
    return field.id


def jsonp_response(**kw):
    debug('JSONP response %s' % kw, 3)
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

PRIVATE_BS_PARAMS = ['bs_private', 'callback', 'key']


def get_formparameters(params):
    d = {}
    for k, v in params.iteritems():
        if k not in PRIVATE_BS_PARAMS:
            if not isinstance(v, basestring):
                value = v.filename
            elif not isinstance(v, (list, set)):
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
