# -*- coding: utf-8 -*-
from tg import expose, url
from bs.lib import base
import urllib2
import urllib
import tg
import json


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
        # serve result on visual_index.mak template file
        return {'oplist': operation_list, 'serv': bs_server_url, 'method': meth}

    @expose('mako:bs.templates.visual_get')
    def get(self, id, *args, **kw):
        """
        Display the plugin form
        by it's id
        """
        # get BioScript server url
        bs_server_url = tg.config.get('main.proxy') + '/'
        # construct request to send to bioscript server
        bs_url = bs_server_url + 'plugins/get?id=' + id
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
        form = urllib2.urlopen(url=bs_url, data=post_data).read()
        # display the form in template
        return {'bs': form,  'bs_server_url': bs_server_url}
