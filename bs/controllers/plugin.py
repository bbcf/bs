# -*- coding: utf-8 -*-
import json
import tg
import os
import urllib2
import urllib
from tg import expose, response
import copy

from bs.lib import base
from bs.lib import services
from bs.lib import constants
from bs.lib import logger
from bs.lib import util
from bs.lib import filemanager
from bs.lib import operations
from bs.lib.operations import wordlist

from bs.celery import tasks
from bs.model import DBSession, PluginRequest, Plugin, Job, Result, Task

import tw2.core as twc
import tw2.forms as twf
import tw2.bs as twb
import tw2.bs.widgets
tw2.bs.widgets.DEBUG = True

DEBUG_LEVEL = 20
TIME_IT = 1


def debug(s, t=0, l=10):
    if DEBUG_LEVEL > l:
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
            d = {'plugins': operations.get_plugins_path(service=user, ordered=ordered)}
        else:
            d = {'plugins': operations.get_plugins_path(ordered=ordered)}
        return d

    @expose('mako:bs.templates.plugin_form')
    @logger.identify
    @logger.log_connection
    @logger.timeit(TIME_IT)
    def fetch(self, oid, *args, **kw):
        """
        Display the form by it's id
        """
        # check plugin id
        plug = None
        try:
            plug = operations.get_plugin_byId(oid)
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
    @expose('mako:bs.templates.plugin_validate')
    def _validate(self, **kw):
        debug('_validate %s' % kw, 4)
        bs_private = copy.deepcopy(json.loads(kw['bs_private']))
        plugin_id = bs_private['pp']['id']
        plug = operations.get_plugin_byId(plugin_id)
        obj = plug
        info = obj.info
        form = info.get('output')()

        if 'prefill' in bs_private:
            prefill_fields(info.get('in'), form, bs_private['prefill'], kw, replace_value=False)
            debug('prefill in validation', 3)
            del bs_private['prefill']

        response.headers['Access-Control-Allow-Headers'] = 'X-CSRF-Token'
        response.headers['Access-Control-Allow-Origin'] = '*'
        form = form().req()
        try:
            form.validate(kw)
        except twc.ValidationError as e:
            main_proxy = tg.config.get('main.proxy')
            e.widget.action = main_proxy + tg.url('plugins/fetch', {'oid': plugin_id})
            util.print_traceback()
            return {'page': 'plugin', 'desc': info.get('description'), 'title': info.get('title'), 'widget': e.widget}
        return 'validated'

    # def _validation_render(self, private_params, plugin, **kw):
    #     """
    #     NOT USED FOR THE MOMENT BUT WILL REPLACE THE INTERNAL CALL IF POSSIBLE
    #     """
    #     form = plugin.info.get('output')()
    #     if 'prefill' in private_params:
    #         prefill_fields(plugin.info.get('in'), form, private_params['prefill'], kw, replace_value=False)
    #         debug('prefill in validation', 3)

    #     form = form().req()
    #     try:
    #         form.validate(kw)
    #     except (twc.ValidationError, Exception) as e:
    #         print 'Validation error %s' % e
    #         response.headers['Access-Control-Allow-Headers'] = 'X-CSRF-Token'
    #         response.headers['Access-Control-Allow-Origin'] = '*'
    #         main_proxy = tg.config.get('main.proxy')
    #         print kw
    #         util.print_traceback()
    #         e.widget.action = main_proxy + tg.url('plugins/fetch', {'oid': private_params['pp']['id']})
    #         return {'page': 'plugin', 'desc': plugin.info.get('description'), 'title': plugin.info.get('title'), 'widget': e.widget}, e.message
    #     return 'validated', 0
    @expose()
    @logger.identify
    @logger.log_connection
    @logger.timeit(TIME_IT)
    def validate(self, **kw):
        """
        plugin parameters validation
        """
        user = util.get_user(tg.request)
        if not 'bs_private' in kw:
            debug('bs_private not found')
            tg.abort(400, "Plugin identifier not found in the request.")
        bs_private = copy.deepcopy(json.loads(kw['bs_private']))

        debug('private %s' % bs_private, 1)
        plugin_id = 0
        try:
            plugin_id = bs_private['pp']['id']
        except KeyError:
            tg.abort(400, "Plugin identifier not found in the request.")
        if plugin_id == 0:
            tg.abort(400, "Plugin identifier not found in the request.")
        plug = operations.get_plugin_byId(plugin_id)
        if plug is None:
            tg.abort(400, "Bad plugin identifier.")

        debug('VALIDATE')
        info = plug.info
        plugin_db = DBSession.query(Plugin).filter(Plugin.generated_id == plug.unique_id()).first()
        plugin_request = _log_form_request(plugin_id=plugin_db.id, user=user, parameters=kw)
        debug('User : %s on plugin: %s' % (user, plugin_id), 2)

        # validate
        request_url = tg.config.get('main.proxy') + '/plugins/_validate'
        form = urllib2.urlopen(request_url, urllib.urlencode(kw)).read()

        #val, error = self._validation_render(bs_private, plug, **kw)
        callback = kw.get('callback', 'callback')
        if form != 'validated':
            #from pylons.templating import render_mako as render
            #form = render('bs/templates/plugin_validate.mak', val)
            debug('validation failed', 2)
            plugin_request.status = 'FAILED'
            plugin_request.error = 'Form validation failed'
            DBSession.add(plugin_request)
            return json.dumps({'validation': 'failed',
                               'desc': info.get('description'),
                               'title': info.get('title'),
                               'widget': form,
                               'callback': callback})

        #remove private parameters from the request
        if 'bs_private' in kw:
            del kw['bs_private']
        if 'key' in kw:
            del kw['key']

        # validation passed
        debug('validated', 2)
        info = plug.info

        # fetch files if any
        debug('fetching files ...', 2)
        try:
            inputs_directory = filemanager.fetch(user, plug, kw)
        except Exception as e:
            debug('not ok', 3)
            plugin_request.status = 'FAILED'
            plugin_request.error = str(e)
            DBSession.add(plugin_request)
            util.print_traceback()
            return json.dumps({'validation': 'success',
                               'desc': info.get('description'),
                               'title':  info.get('title'),
                               'error': 'error while fetching files : ' + str(e),
                               'callback': callback})
        debug('ok', 3)

        # get output directory to write results
        outputs_directory = filemanager.temporary_directory(constants.paths['data'])
        service_callback = None
        if user.is_service:
            debug('is service', 1)
            # def out_path(service_name):
            o = services.service_manager.get(user.name, constants.SERVICE_RESULT_ROOT_PARAMETER)
            if o:
                outputs_directory = o
            service_callback = services.service_manager.get(user.name, constants.SERVICE_CALLBACK_URL_PARAMETER)

        debug('Write result in %s' % outputs_directory, 2)
        # get user parameters from the request
        user_parameters = bs_private.get('app', "{}")

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
        debug('Launch task %s' % task_id, 2)

        _log_job_request(plugin_request.id, task_id)

        resp = {'validation': 'success',
                'plugin_id': plugin_id,
                'task_id': task_id,
                'callback': callback,
                'app': user_parameters}
        if resp_config and resp_config.get('plugin_info', '') == 'min':
            resp.update({'plugin_info': json.dumps({'title': info['title'],
                                                    'description': info['description'],
                                                    'path': info['path'],
                                                    'in': info['in'],
                                                    'out': info['out'],
                                                    'meta': info['meta']})})
        return json.dumps(resp)

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
    debug('PREFILL FIELDS')
    for type_to_prefill, prefill_with in prefill_params.iteritems():
        debug('type, prefill: %s, %s' % (type_to_prefill, prefill_with), 2)
        for fparam in form_parameters:
            debug('Checking parameter %s' % fparam, 2)

            if wordlist.is_of_type(fparam.get('type'), type_to_prefill):
                debug('prefilling ...', 3)
                fid = fparam.get('id')

                # when validation occurs, there no need to replace parameters
                if replace_value:
                    kw[fid] = prefill_with

                # if fparam is of `file` type, we need to modify it
                if wordlist.is_of_type(fparam.get('type'), wordlist.FILE):
                    debug('change file field ...', 3)

                    multiple = fparam.get('multiple', False)
                    #TODO utility method to get all children
                    for field in form.children_deep():
                        if field.id == fid or fid.startswith('%s:' % field.id):
                            if multiple:
                                mod = _change_file_field(form, field, twf.BsMultiple, prefill_with)
                            else:
                                mod = _change_file_field(form, field, twb.BsTripleFileField, prefill_with)
                            modified.append(mod)
        return modified


def set_validator(validator, field):
    required = False
    strip = False
    try:
        required = validator.required
    except AttributeError:
        pass
    try:
        strip = validator.strip
    except AttributeError:
        pass
    if 'BsTripleFileField' in str(field):
        field.validator = twb.BsFileFieldValidator(required=required, strip=strip)
    elif 'BsMultiple' in str(field):
        field.validator = twb.MultipleValidator(required=required, strip=strip)
    else:
        field.validator = twc.Validator(required=required, strip=strip)


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
    # if hasattr(field, 'label'):
    #     tmp.label = field.label
    # else:
    #     tmp.label = field.id
    debug('change file field', 1)
    if field.validator is not None:
        set_validator(field.validator, tmp)
    try:
        tmp.name = field.name
    except AttributeError:
        tmp.name = field.key
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
    debug(tmp_parent)
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
    #form = tmp_form
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

PRIVATE_BS_PARAMS = ('bs_private', 'callback', 'key')


def get_formparameters(params):
    d = {}
    for k, v in params.iteritems():
        if k not in PRIVATE_BS_PARAMS:
            d[k] = _get_value(v)
    return d


def _get_value(param):
    if isinstance(param, (list, tuple)):
        value = [_get_value(p) for p in param]
    elif not isinstance(param, basestring):
        value = param.filename
    else:
        value = str(param)
    return value


def _log_job_request(request_id, task_id):
    job = Job()
    job.request_id = request_id
    job.task_id = task_id
    DBSession.add(job)
    return job
