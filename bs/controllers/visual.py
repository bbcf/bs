# -*- coding: utf-8 -*-
from tg import request, expose, url, flash, response, require
from tg.controllers import redirect
from bs.lib.base import BaseController
from bs import handler
from repoze.what.predicates import has_permission
from pylons import tmpl_context
import urllib2, urllib
import tg
import json



class VisualController(BaseController):
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
        bs_server_url = tg.config.get('main.proxy') + url('/')
        # build request to send to BioScript server
        bs_url =  bs_server_url + 'plugins?ordered=true'
        # get the operation list back
        operation_list = urllib2.urlopen(bs_url).read()
        # fields can be pre-filled
        meth = 'get'
        if len(args)> 0 and args[0] == 'prefill': meth = 'get_prefill'
        # serve result on visual_index.mak template file
        return {'oplist' : operation_list, 'serv' : bs_server_url, 'method' : meth}


    @expose('mako:bs.templates.visual_get')
    def get(self, id, *args, **kw):
        """
        Display the plugin form
        by it's id
        """
        # get BioScript server url
        bs_server_url = tg.config.get('main.proxy') + url('/')
        # construct request to send to bioscript server
        bs_url =  bs_server_url + 'plugins/get?id=' +  id
        # get the form back
        form = urllib2.urlopen(bs_url).read()
        # display the form in template
        return {'bs' : form,  'bs_server_url' : bs_server_url}

    @expose('mako:bs.templates.visual_get')
    def get_prefill(self, id, *args, **kw):
        """
        The same method as 'get' but here we want
        to pre-fill 'file' fields with data.
        """
        bs_server_url = tg.config.get('main.proxy') + url('/')
        bs_url =  bs_server_url + 'plugins/get?id=' +  id

        # we want to prefill 'file' fields
        # here we generate test data
        # data is formatted like that : [(file_url, file_name), (file_url, file_name), ...]
        file_url = tg.config.get('main.proxy') + url('/test')
        prefill_data = [(file_url + '/' + fname, fname) for fname in ('file1.txt', 'file2.txt', 'file3.txt')]
        # as we don't really which form will be displayed
        # we tell to prefill "file" field type.
        prefill = {'prefill' : json.dumps({'file' : prefill_data})}
        post_data = urllib.urlencode(prefill)
        # get the form back  send via POST
        form = urllib2.urlopen(url=bs_url, data=post_data).read()
        # display the form in template
        return {'bs' : form,  'bs_server_url' : bs_server_url}




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
#
#        # map field id to boolean multiple if file is `file` type
#        # need to distinguish between simple and multiple select fields
#        d = dict( [(param.get('id'), param.get('multiple', False)) for param in in_params if wordlist.is_of_type(param.get('type'), wordlist.FILE)])
#
#        prefill = json.loads(kw.get('prefill'))
#        for key, value in prefill.iteritems():
#            for param in in_params:
#                if wordlist.is_of_type(param.get('type'), key):
#                    kw[param.get('id')] = value
#
#
#
#    # change field if it's multiple or simple only if it's a `file` field
#    # (will only do it if it's from a service that have prefilled information)
##    for index, field in enumerate(fields):
##        fid = field.id
##        if d.has_key(fid):
##            if d.get(fid) : _process_file_field(user, form, field, kw, tw2.forms.MultipleSelectField, index, False)
##            else          : _process_file_field(user, form, field, kw, tw2.forms.SingleSelectField, index, True)
#
#
#    # add form private parametersoperation_list
#    pp = {}
#    pp['id']=id
#    kw['pp']=json.dumps(pp)
#    return kw
#
#def _fill_fields(field, field_id, params):
#    """
#    Fill field options with pre-filled values
#    """
#    _list = params.get(field_id, "[]")
#    if len(_list)>0:
#        if isinstance(_list[0], (list, tuple)):
#            field.options = [(_list[i][0], _list[i][1]) for i in xrange(len(list(_list)))]
#        else :
#            field.options = dict([(_list[i], _list[i]) for i in xrange(len(list(_list)))])
#    else :
#        field.options=[]
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



