# -*- coding: utf-8 -*-
from tg import expose, session, redirect
from bs.lib import base
import urllib2
import urllib
import tg
import json
from bs.lib import operations
from bs.model import DBSession, Job


class DirectController(base.BaseController):
    """
    Display plugins operation and forms when
    user come directly to BioScript server
    """

    @expose('mako:bs.templates.visual_index')
    def index(self, *args):
        """
        Display a list of all plugins in BioScript
        """
        # get BioScript Server url (usually from config file)
        bs_server_url = tg.config.get('main.proxy') + '/'
        # build request to send to BioScript server
        bs_url = bs_server_url + 'plugins?ordered=true'
        # get the operation list back
        operation_list = urllib2.urlopen(bs_url).read()
        # fields can be pre-filled
        meth = 'get'
        if len(args) > 0 and args[0] == 'prefill':
            meth = 'get_prefill'
        # get previous launched jobs taht are in the session
        task_ids = session.get('task_ids', [])
        jobs = []
        if task_ids:
            jobs = DBSession.query(Job).filter(Job.task_id.in_(task_ids)).all()
        # serve result on visual_index.mak template file
        return {'oplist': operation_list, 'serv': bs_server_url, 'method': meth, 'jobs': jobs}

    @expose('mako:bs.templates.visual_get')
    def get(self, id, *args, **kw):
        """
        Display the plugin form
        by it's id
        """
        # get BioScript server url
        bs_server_url = tg.config.get('main.proxy') + '/'
        # construct request to send to bioscript server
        bs_url = bs_server_url + 'plugins/fetch?oid=' + id
        # get the form back
        form = urllib2.urlopen(bs_url).read()
        # display the form in template
        return {'bs': form,  'bs_server_url': bs_server_url}

    @expose('mako:bs.templates.visual_get')
    def get_prefill(self, id, *args, **kw):
        """
        The same method as 'get' but here we want
        to pre-fill 'file' fields with data.
        """
        bs_server_url = tg.config.get('main.proxy') + '/'
        bs_url = bs_server_url + 'plugins/fetch?oid=' + id

        # private parameter that you want to get back when the form is submitted
        # to bs and the validation success (the operation is launched)
        private_params = {"my_user": 'someuserid', "private_parameter": 'someotherparameter'}

        # add some configuration to send to bioscript
        # 'key' is the shared unique key between bioscript and your application
        # if you have configured an access
        # 'plugin_info' can be set to 'min' if you don't want all the plugin information
        # back in the response
        cfg = {'plugin_info': 'full'}
        key = 'somekey'
        # then we want to prefill the 'file' fields in the form
        # here we generate a test data formatted like that : [(file_url, file_name), (file_url, file_name), ...]
        # (a list containing for each item, the url of the file an it's name)
        file_url = tg.config.get('main.proxy') + '/test'
        prefill_data = {'file': [(file_url + '/' + fname, fname) for fname in ('file1.txt', 'file2.txt', 'file3.txt')]}

        # put all this parameters under the 'bs_private' parameter
        parameters = {
            'key': key,
            'bs_private': json.dumps({
                'app': private_params,
                'cfg': cfg,
                'prefill': prefill_data
        })}
        # here we delete the 'key' parameters because it's an exemple and
        # there is not customized access
        del parameters['key']

        # # prepare the POST data
        post_data = urllib.urlencode(parameters)

        # get the form back  send via POST
        form = urllib2.urlopen(url=bs_url, data=post_data).read()
        # display the form in template
        return {'bs': form,  'bs_server_url': bs_server_url}

    @expose('mako:bs.templates.visual_status')
    def status(self):
        jobs = DBSession.query(Job).all()
        plugins = operations.get_plugins_path()
        mapping = {'plugins': plugins, 'nbplugins': len(plugins), 'total': len(jobs), 'running': 0, 'failure': 0, 'pending': 0, 'success': 0}
        for job in jobs:
            mapping[job.status.lower()] += 1
        return mapping

    @expose()
    def success(self, task_id):
        task_ids = session.get('task_ids', [])
        task_ids.append(task_id)
        session['task_ids'] = task_ids
        session.save()
        raise redirect('/jobs?task_id=%s' % task_id)
