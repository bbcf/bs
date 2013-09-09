# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json
import tg
import os
import urllib2
import urllib
from tg import expose, response
import copy
import re

from bs.lib import base
from bs.lib import services
from bs.lib import constants
from bs.lib import logger
from bs.lib import util
from bs.lib import filemanager
from bs.lib import operations
from bs.lib.operations import wordlist
import cgi
from bs.celery import tasks
from bs.model import DBSession, PluginRequest, Plugin, Job, Result, Task

import tw2.core as twc
import tw2.bs as twb
import tw2.bs.widgets

tw2.bs.widgets.DEBUG = True

multipattern = re.compile('(\w+):(\d+):(\w+)')
DEBUG = True
TIME_IT = 1

class SparseList(list):
    def __setitem__(self, index, value):
        missing = index - len(self) + 1
        if missing > 0:
            self.extend([None] * missing)
        list.__setitem__(self, index, value)

def debug(s):
    if DEBUG:
        print s


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
        debug('\n[plugin controller]FETCH')
        # check plugin id
        plug = None
        try:
            plug = operations.get_plugin_byId(oid)
        except:
            tg.abort(400, "Bad plugin identifier")

        debug('[x] get plugin %s' % oid,)
        # get the plugin
        obj = plug
        info = obj.info
        form = info.get('output')()
        desc = plug.description_as_html

        debug('[x] params =  %s' % kw,)
        # bioscript parameters
        bs_private = {}
        if 'bs_private' in kw:
            bs_private = json.loads(kw['bs_private'])
            debug("[x] get bs private parameters %s" % bs_private,)

        if 'prefill' in bs_private:
            prefill_fields(info.get('in'), form, bs_private['prefill'], kw)

        # add some private parameters from BioScript
        pp = {'id': oid}
        # if user is a service, add the key & the mail in the authentication
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
        debug('END FETCH')
        html_doc = ''
        html_src_code = ''
        try:
            html_doc = obj.html_doc_link()
            html_src_code = obj.html_source_code_link()
        except Exception as e:
            print '"html_doc" and "src_code" seems to be missing for your plugin, please update bsplugins to the last version'
            print e

        return {'page': 'plugin', 'desc': desc, 'title': info.get('title'), 'widget': widget, 'html_doc': html_doc, 'html_src_code': html_src_code}

    @expose()
    @expose('mako:bs.templates.plugin_validate')
    def _validate(self, **kw):
        debug('_validate %s' % kw,)
        bs_private = copy.deepcopy(json.loads(kw['bs_private']))
        plugin_id = bs_private['pp']['id']
        plug = operations.get_plugin_byId(plugin_id)
        obj = plug
        info = obj.info
        form = info.get('output')()

        # prefilling form (if the validation fail, respons must contain the form prefilled
        # perhaps we can do this only if the form validation fail)
        if 'prefill' in bs_private:
            prefill_fields(info.get('in'), form, bs_private['prefill'], kw, replace_value=False)
            debug('prefill in validation',)
            del bs_private['prefill']

        response.headers['Access-Control-Allow-Headers'] = 'X-CSRF-Token'
        response.headers['Access-Control-Allow-Origin'] = '*'
        form = form().req()
        try:
            kw = form.validate(kw)
        except twc.ValidationError as e:
            main_proxy = tg.config.get('main.proxy')
            e.widget.action = main_proxy + tg.url('plugins/fetch', {'oid': plugin_id})
            util.print_traceback()
            return {'page': 'plugin', 'desc': info.get('description'), 'title': info.get('title'), 'widget': e.widget}
        return json.dumps({'validated': True, 'params': kw})

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
    #         print kw§
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
        # get private bioscript parameters
        if not 'bs_private' in kw:
            debug('bs_private not found')
            tg.abort(400, "Plugin identifier not found in the request.")
        bs_private = copy.deepcopy(json.loads(kw['bs_private']))

        debug('\n[plugin controller]\nVALIDATE %s' % kw,)


        # get the plugin from the private parameters
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

        # get the plugin from database
        plugin_db = DBSession.query(Plugin).filter(Plugin.generated_id == plug.unique_id()).first()

        


        # validate the form
        # we must do an HTTP call because I don't find a way
        # to call the 'render' method on 'plugin_validate' template
        request_url = tg.config.get('main.proxy') + '/plugins/_validate'
        validated = True
        info = plug.info
        # get the callback if any
        callback = kw.get('callback', 'callback')
        try:
            form = urllib2.urlopen(request_url, urllib.urlencode(kw)).read()

            # add some header because the request can come from another domain
            response.headers['Access-Control-Allow-Headers'] = 'X-CSRF-Token'
            response.headers['Access-Control-Allow-Origin'] = '*'

            
            try:
                form = json.loads(form)
            except:
                pass
           
            validated = isinstance(form, dict)


        except Exception as e:
            util.print_traceback()
            validated = False
            form = 'Problem with Bioscript server.'

        if not validated:
            debug('Validation failed',)
            return json.dumps({'validation': 'failed',
                               'desc': info.get('description'),
                               'title': info.get('title'),
                               'widget': form,
                               'callback': callback})

        # validation passes
        new_params = form['params']
        new_params = kw
        debug('Validation passes with params : %s' % new_params,)

        # we regoup all multi stuff in a single list:
        # for instance a multi field will give parameters like:
        # {SigMulti:1:signals: val1, SigMulti:2:signals: val2, ...}
        # and we will transform it to
        # {SigMulti: { signals : [val1, val2], ...}
        
        grouped_params = {}
        todel = []
        for k, v in new_params.iteritems():
            m = multipattern.match(k)
            print 'doing : %s (%s)' % (k, v)
            if m:
                todel.append(k)
                if v:
                    key1, n, key2 = m.groups()
                    if not key1 in grouped_params:
                        grouped_params[key1] = {}
                    if key2 in grouped_params[key1]:
                        grouped_params[key1][key2][int(n) - 1] = v
                    elif not key2.endswith('bs_group'):
                        sl = SparseList()
                        sl[int(n) - 1] = v
                        grouped_params[key1][key2] = sl

        debug('group "multi" params: %s' % grouped_params)
        # debug('check fieldstorages',)
        # # must keep fieldstorages because they were converted to str
        # fs_bk = []
        # import cgi
        # for k, v in kw.iteritems():
        #     if isinstance(v, cgi.FieldStorage):
        #         fs_bk.append((k, v))
        # debug(fs_bk)

        # for fsk, fsv in fs_bk:
        #     m = multipattern.match(fsk)
        #     if m:
        #         key1, n, key2 = m.groups()
        #         grouped_params[key1][key2][int(n) - 1] = fsv
        #     else:
        #         grouped_params[fsk] = fsv
        new_params.update(grouped_params)
        
        # delete multi parameters
        for td in todel:
            del new_params[td]

        # but we need to keep all params that are multi and urls
        kw = new_params
       
        #remove private parameters from the request
        if 'bs_private' in kw:
            del kw['bs_private']
        if 'key' in kw:
            del kw['key']

        debug('New params are : %s' % new_params,)

        # update plugin arameters
        # log the request, it's a valid one
        plugin_request = _log_form_request(plugin_id=plugin_db.id, user=user, parameters=dict(kw))
        DBSession.add(plugin_request)
    
        debug('get output directory',)
        # get output directory to write results
        outputs_directory = filemanager.temporary_directory(constants.paths['data'])
        service_callback = None
        # if the user is a service, get parameters from configuration
        if user.is_service:
            debug('is service',)
            o = services.service_manager.get(user.name, constants.SERVICE_RESULT_ROOT_PARAMETER)
            if o:
                outputs_directory = o
            service_callback = services.service_manager.get(user.name, constants.SERVICE_CALLBACK_URL_PARAMETER)
        debug('Write result in %s' % outputs_directory,)
        

        # get prvate parameters from the request
        private_parameters = bs_private.get('app', "{}")

        # get response configuration from the request
        resp_config = bs_private.get('cfg', None)
        plugin_info = {'title': info['title'],
                       'plugin_id': plugin_db.id,
                       'generated_id': plugin_db.generated_id,
                       'description': info['description'],
                       'path': info['path'],
                       'in': info['in'],
                       'out': info['out'],
                       'meta': info['meta']}

        # define the bioscript callback
        bioscript_callback = tg.config.get('main.proxy') + '/' + tg.url('plugins/callback_results')
        debug("callback on bs : %s " % bioscript_callback,)

        # if some files come from a file field, we must download them directly
        inputs_directory, dwdfiles = filemanager.fetchfilefields(user, plug, kw)

        # chain jobs : fetch files then plugin process
        async_res = tasks.plugin_job.delay(user,
                                   plug,
                                   inputs_directory,
                                   outputs_directory,
                                   dwdfiles,
                                   plugin_info,
                                   private_parameters,
                                   service_callback,
                                   bioscript_callback,
                                   **kw)

        task_id = async_res.task_id
        debug('Launch task %s' % task_id,)

        # log the job request
        _log_job_request(plugin_request.id, task_id)

        #prepare the response
        resp = {'validation': 'success',
                'plugin_id': plugin_id,
                'task_id': task_id,
                'callback': callback,
                'app': private_parameters}
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
        print 'CALLBACK %s %s' % (task_id, results)
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
    debug('\nPREFILL FIELDS')
    for type_to_prefill, prefill_with in prefill_params.iteritems():
        debug('type, prefill: %s, %s' % (type_to_prefill, prefill_with),)
        for fparam in form_parameters:
            #debug('Checking parameter %s' % fparam,)

            if wordlist.is_of_type(fparam.get('type'), type_to_prefill):
                fid = fparam.get('id')
                #debug('prefilling "%s" ... ' % fid,)

                # when validation occurs, there no need to replace parameters (replace_value = False)
                if replace_value:
                    kw[fid] = prefill_with
                #debug(kw,)
                # if fparam is of `file` type, we need to modify it
                if wordlist.is_of_type(fparam.get('type'), wordlist.FILE):
                    #debug('change file field ...', 3)

                    #multiple = fparam.get('multiple', False)
                    #TODO utility method to get all children
                    for child_index, field in enumerate(form.children_deep()):
                        #debug('test %s' % field, 3)
                        if field.id == fid or fid.startswith('%s:' % field.id) and 'BsFileField' in str(field):
                           # if multiple:
                                #mod = _change_file_field(form, field, twb.BsMultiple, prefill_with)
                            #else:
                            mod = _change_file_field(form, field, twb.BsTripleFileField, prefill_with, child_index)
                            modified.append(mod)
                        # fetch children for this field if any and if not already replaced
                        # it 's not recursive and should bs
                        else:
                            mod = recursivly_check_and_change_field_children(field, fid, form, prefill_with, child_index)
                            if mod:
                                modified.append(mod)
    debug('\n')
    return modified


def recursivly_check_and_change_field_children(field, fid, form, prefill_with, child_index, deep=0):
    if hasattr(field, 'child') and hasattr(field.child, 'children') and len(field.child.children) > 0:
        deep += 1
        for c in field.child.children:
            #debug('test deep : %s' % c, 4)
            if c.id == fid or fid.startswith('%s:' % c.id) and 'BsFileField' in str(c):
                mod = _change_file_field(form, c, twb.BsTripleFileField, prefill_with, child_index, deep)
                return mod
            else:
                mod = recursivly_check_and_change_field_children(c, fid, form, prefill_with, child_index, deep)
                if mod:
                    return mod


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
    if 'BsTripleFileField' in str(field) or 'BsFileField' in str(field):
        field.validator = twb.BsFileFieldValidator(required=required, strip=strip)
    # elif 'BsMultiple' in str(field):
    #     field.validator = twb.BsMultipleValidator(required=required, strip=strip)
    else:
        field.validator = twc.Validator(required=required, strip=strip)


def _change_file_field(form, field, clazz, value, index, deep=0):
    """
    Modify field type
    :param form: the 'form widget'
    :param field: the field to modify
    :param clazz: the clazz to replace the field with
    :param index: the position of the field in the form
    :param value: fill the new field with "value"
    :param deepe: how "deep" is the child
    """

    # prepare
    tmp = clazz()
    tmp.id = field.id
    #debug('change file field', 1)

    # transmit validator
    if field.validator is not None:
        set_validator(field.validator, tmp)

    # transmit help text
    try:
        tmp.help_text = field.help_text
    except AttributeError:
        pass

    # transmit name
    try:
        tmp.name = field.name
    except AttributeError:
        tmp.name = field.key
    try:
        tmp.label = field.label
    except AttributeError:
        tmp.label = field.key

    # transmit options if any
    if len(value) > 0:
        if isinstance(value[0], (list, tuple)):
            tmp.options = [(value[i][0], value[i][1]) for i in xrange(len(list(value)))]
        else:
            tmp.options = dict([(value[i], value[i]) for i in xrange(len(list(value)))])
    else:
        tmp.options = []

    # replace with th clazz provided
    # we need here to take the right index
    # in the form.
    #print 'replace %s with %s' % (field, clazz)
    if deep == 0:
        form.child.children[index] = tmp
    else:
        # Warning : it is not recursive and just checjk the first children
        for cindex, child in enumerate(form.child.children[index].child.children):
            if 'BsFileField' in str(child):
                form.child.children[index].child.children[cindex] = tmp


    # tmp_parent = field.parent
    # debug(tmp_parent)
    # parent_deep = 1
    # tmp_form = form
    # #print tmp_parent
    # while(tmp_parent != form):
    #     tmp_parent = tmp_parent.parent
    #     #print tmp_parent
    #     parent_deep += 1
    #     tmp_form = tmp_form.child

    # for index, f in enumerate(tmp_form.children):
    #     if f.id == field.id:
    #         tmp_form.children[index] = tmp
    #form = tmp_form
    return field.id


def jsonp_response(**kw):
    debug('JSONP response %s' % kw,)
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
    pl.status = 'PENDING'
    params = get_formparameters(parameters)
    debug('set request params %s' % params,)
    #print ', '.join(['%s (%s) : %s (%s)' % (k, type(k), v, type(v)) for k, v in params.iteritems()])
    pl.parameters = params
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
        value = [copy.copy(_get_value(p)) for p in param]
    elif isinstance(param, int):
        value = str(param)
    elif isinstance(param, cgi.FieldStorage):
        value = param.filename
    elif isinstance(param, dict):
        value = {}
        for _k, _v in param.iteritems():
            value[_k] = _get_value(_v)
    else:
        value = copy.copy(str(param))
    return value


def _log_job_request(request_id, task_id):
    job = Job()
    job.request_id = request_id
    job.task_id = task_id
    DBSession.add(job)
    return job
