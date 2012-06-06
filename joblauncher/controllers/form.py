# -*- coding: utf-8 -*-
from tg import request, expose, url, flash, response, require
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
import tg
from paste.request import get_cookies
__all__ = ['FormController']
import tw2.forms
to_treat_as_file_list = {'SingleSelectField' : False, 'MultipleSelectField' : True}

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
    index = -1
    for field in fields:
        index += 1
        if field.id in files:
            if not user.is_service:
                # put a fileField instead of the selectField
                tmp = tw2.forms.FileField()
                tmp.id = field.id
                form.child.children[index] = tmp
            else :
                _list = json.loads(kw.get(field.id, "[]"))
                if len(_list)>0:
                    if isinstance(_list[0], list):
                        print [(_list[i], _list[i]) for i in xrange(len(list(_list)))]
                        field.options = [(_list[i][0], _list[i][1]) for i in xrange(len(list(_list)))]
                    else :
                        field.options = dict([(_list[i], _list[i]) for i in xrange(len(list(_list)))])
                else :
                    field.options=[]

    value = {}
    for k, v in kw.iteritems():
        value[k]=v

    # edit private parameters
    if kw.has_key('key'):
        value['key']=kw.get('key')
    if kw.has_key('up'):
        value['up']=kw.get('up')

    pp = {}
    pp['id']=id
    value['pp']=json.dumps(pp)


    return value

class FormController(BaseController):

    @expose('json')
    @expose('joblauncher.templates.form_list')
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




    @expose('joblauncher.templates.plugin_form')
    def index(self, id, *args, **kw):
        """
        Method to get the form
        """

        # get the plugin
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))

        obj = plug.plugin_object
        form =  obj.output()

        user = handler.user.get_user_in_session(request)
        value = parse_parameters(user, id, form, obj.files(), **kw)




        main_proxy = tg.config.get('main.proxy')
        widget = form(action= main_proxy + url('/form/launch')).req()
        widget.value = value
        return {'page' : 'form', 'title' : obj.title(), 'widget' : widget}


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


        ### VALIDATE ###
        try:
            print 'validation'
            form.validate(kw)
        except Invalid as e:
            import traceback, sys
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            flash(e, 'error')
            raise redirect(url('./index', params={'id' : form_id}))
        print 'get user'
        user = handler.user.get_service_in_session(request)
        print 'fetching files'
        ### FETCH FILES ###
        try :
            if user.is_service :
                tmp_dir = services.io.fetch_files(user, plug.plugin_object.files(), kw)
            else :
                tmp_dir = services.io.fetch_file_field(user, plug.plugin_object.files(), kw)
                print tmp_dir
                raise Exception('blou')
        except Exception as e:
            flash(e, 'error')
            raise redirect(url('./index', params={'id' : form_id}))
        print 'fetched'
        service = user.name

        out_path = services.io.out_path(service)
        callback_url = services.service_manager.get(service, constants.SERVICE_CALLBACK_URL_PARAMETER)
        print 'launch process'
        ### PLUGIN PROCESS ###
        async_res = tasks.plugin_process.delay(form_id, service, tmp_dir, out_path, plug.plugin_object.title(), plug.plugin_object.description(), callback_url, **kw)

        task_id = async_res.task_id
        ### UPDATE DB ###
        handler.database.new_request(kw, task_id, out_path)

        flash('Job launched')
        raise redirect(url('./done',  {'task_id' : task_id}))

    @expose()
    def done(self, *args, **kw):
        return '%s' % ( kw)

    @expose('json')
    @expose('joblauncher.templates.form_info')
    def info(self, id):
        plug = plugin.get_plugin_byId(id)
        if plug is None:
            raise redirect(url('./error', {'bad form id' : id}))
        o = plug.plugin_object
        info = o.description()
        title = o.title()
        params = o.parameters()

        return {'page' : 'form', 'info' : info, 'title' : title, 'parameters' : params, 'id' : id}


