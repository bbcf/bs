# -*- coding: utf-8 -*-
from tg import expose, url
from bs.lib import base
import urllib2
import urllib
import tg
import json


class DevController(base.BaseController):
    """
    Show the simplest example for developpers
    """

    @expose('mako:bs.templates.dev_index')
    def index(self, *args):
        """
        Display a list of all plugins in BioScript
        """
        # Get BioScript Server url (usually from config file)
        bs_server_url = tg.config.get('main.proxy') + '/'

        # Fetch the list of operations
        # (if you have a defined service, add your key in the request body to fetch
        # only operations you defined)
        bs_url = bs_server_url + 'plugins?ordered=true'
        operation_list = urllib2.urlopen(bs_url).read()

        # define other parameters
        # bs_server url
        validation_url = url('/devs/validation')
        get_url = url('/devs/get')
        return {'oplist': operation_list, 'bs_serv_url': bs_server_url, 'validation_url': validation_url, 'gurl': get_url}

    @expose()
    def get(self, id, *args, **kw):
        """
        The method to get the form from BioScript server.
        """
        bs_server_url = tg.config.get('main.proxy') + '/'
        bs_url = bs_server_url + 'plugins/get?id=' + id

        # we want to prefill 'file' some fields in the form
        # aka we want to prefill FileField with SingleSelectField with
        # files from our application
        # here we generate test data
        # data is formatted like that : [(file_url, file_name), (file_url, file_name), ...]
        file_url = tg.config.get('main.proxy') + '/test'
        prefill_data = [(file_url + '/' + fname, fname) for fname in ('file1.txt', 'file2.txt', 'file3.txt')]
        # as we don't really which form will be displayed
        # we tell to prefill "file" field type.
        prefill = {'prefill': json.dumps({'file': prefill_data})}
        post_data = urllib.urlencode(prefill)
        # get the form back  send via POST
        req = urllib2.urlopen(url=bs_url, data=post_data)
        # display the form in template
        return req.read()

    @expose()
    def validation(self, task_id, plugin_id, plugin_info):
        message = 'got validation %s on plugin %s with plugin info : %s' % (task_id, plugin_id, plugin_info)
        # you can remove 'plugin_info' parameter if you pass {'cfg': {'plugin_info': 'min'}} in bs_private parameters
        return message
