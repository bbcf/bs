from bs.lib.operations import wordlist
from bs.lib import constants, services
import tempfile
import os
import shutil
import urlparse
import urllib2
import json
import re
import cgi

block_sz = 2048 * 4


DEBUG_LEVEL = 1


NAME_PATTERN = re.compile('\?.*?name=(?P<name>.+?)(&|$)')
HTS_TYPE_PATTERN = re.compile('\?.*?type=(?P<type>.+?)(&|$)')


class UrlError(Exception):
    pass


def debug(s, inline=True):
    if DEBUG_LEVEL > 0:
        if inline:
            print '[filemanager] %s' % s,
        else:
            print '[filemanager] %s' % s

def temporary_directory(directory=constants.paths['tmp']):
    return tempfile.mkdtemp(dir=directory)

import re

MULTIPLE_PARAMS_PATTERN = re.compile('^\w+:(?P<nb>\d+):(?P<param>\w+)$')


class SparseList(list):
    def __setitem__(self, index, value):
        missing = index - len(self) + 1
        if missing > 0:
            self.extend([None] * missing)
        list.__setitem__(self, index, value)


def regoup_multiple_field_in_list(form_parameters):
    todel = []
    paramlist = {}
    for k, v in form_parameters.iteritems():
        m = MULTIPLE_PARAMS_PATTERN.match(k)
        if m:
            param = m.group('param')
            index = int(m.group('nb')) - 1
            todel.append(k)
            if param not in paramlist:
                paramlist[param] = SparseList()
            paramlist[param][index] = v
    for p in todel:
        del form_parameters[p]
    form_parameters.update(paramlist)


def check_files_parameter(plugin, form_parameters):
    pass

def fetchfilefields(user, plugin, form_parameters):
    """
    Download the file fields and change the form parameters accordingly
    return the directory where file has been downloaded and the dwd files.
    """
    files = plugin.in_params_typeof(wordlist.FILE)
    debug('Download file fields :  %s' % form_parameters)
    root_directory = temporary_directory()
    
    dwdfiles = {}
    for infile in files:
        debug("download '%s' ? " % infile)
        fid = infile.get('id')
        form_value = None
        
        # check if it's a multiple field. In that case we will have a list
        if infile.get('multiple'):
            if isinstance(form_parameters.get(infile['multiple']), dict):
                form_value = form_parameters[infile['multiple']].get(fid)
        else:
            form_value = form_parameters.get(fid)

        # check if form_value contains a value or is not an empty list
        if form_value is not None and (not isinstance(form_value, (list, tuple)) or len(form_value) > 0) and form_value != '':

            # check if we have a list or a single value
            if not isinstance(form_value, (list, tuple)):
                form_value = [form_value]

            for index, v in enumerate(form_value):
                if isinstance(v, cgi.FieldStorage):
                    dwdfile = download_file_field(v, os.path.join(temporary_directory(root_directory), v.filename))

                    # Update form parameters
                    if infile.get('multiple', False):
                        if infile.get('multiple') not in dwdfiles:
                            dwdfiles[infile.get('multiple')] = {}
                        if fid not in dwdfiles[infile.get('multiple')]:
                            dwdfiles[infile.get('multiple')][fid] = SparseList()
                        dwdfiles[infile.get('multiple')][fid][index] = True
                        form_parameters[infile.get('multiple')][fid][index] = dwdfile
                    else:
                        dwdfiles[fid] = True
                        form_parameters[fid] = dwdfile
    debug('File fields downloaded:  %s --- form parameters are : %s' % (dwdfiles, form_parameters))
    return root_directory, dwdfiles

def fetchurls(user, plugin, dwdfiles, root_directory, form_parameters):
    """
    Download the file fields and change the form parameters accordingly
    return the directory where file has been downloaded
    """
    files = plugin.in_params_typeof(wordlist.FILE)
    debug('FETCH from URLS %s' % form_parameters, False)
    for infile in files:
        debug('infile is %s' % infile)
        fid = infile.get('id')
        form_value = None
        # check if it's a multiple field. In that case we will have a list
        if infile.get('multiple'):
            debug('is multiple')
            if isinstance(form_parameters.get(infile['multiple']),dict):
                form_value = form_parameters[infile['multiple']].get(fid)
        else:
            form_value = form_parameters.get(fid)

        # check if form_value contains a value or is not an empty list
        
        if form_value is not None and (not isinstance(form_value, (list, tuple)) or len(form_value) > 0) and form_value != '':
            debug("check parameter")
            # check if we have a list or a single value
            if not isinstance(form_value, (list, tuple)):
                form_value = [form_value]

            for index, val in enumerate(form_value):
                # check if it is not already downloaded
                dwd = False
                multiple = infile.get('multiple', False)
                debug('multiple ? %s' % multiple)
                if multiple:
                    if infile.get('multiple') in dwdfiles:
                         if not dwdfiles[infile.get('multiple')].get(fid, False):
                            dwd = True
                else:
                    if not dwdfiles.get(fid, False):
                        dwd = True
                debug("download ? %s" % dwd)
                if dwd:
                    debug("trying to download")
                    if user.is_service:
                        # the user is a service, as HTSStation, so Urls has to be transformed into path
                        debug('is service',)
                        file_root = services.service_manager.get(user.name, constants.SERVICE_FILE_ROOT_PARAMETER)
                        debug('got file_root : %s' % file_root,)
                        url_root = services.service_manager.get(user.name, constants.SERVICE_URL_ROOT_PARAMETER)
                        debug('got url_root : %s' % url_root,)
                        if file_root is None or url_root is None:
                            _to = _durl(root_directory, form_value, val)
                        else: 
                            _to = _dservice(root_directory, form_value, val, url_root, file_root)
                    else:
                        # user is not a service so URLs are 'real' urls
                        debug('is real user')
                        _to = _durl(root_directory, form_value, val)

                    # Update form parameters
                    if infile.get('multiple', False):
                        form_parameters[infile.get('multiple')][fid][index] = _to
                    else:
                        form_parameters[fid] = _to
                    debug('Done', False)
        else:
            debug('no value for that file', False)
    return root_directory


def _dservice(root_directory, form_value, val, url_root, file_root):
    """
    Download the file(s). As the user is a service, fetch the file from a path.
    """
    debug('fetch from path')
    # remove //. Service defined a directory where to take & put files
    # so the urls are fakes
    fname, val = take_filename_and_path(val)
    val = val.replace('//', '/').replace(':/', '://')
    _from = val.replace(url_root, file_root)
    _to = os.path.join(temporary_directory(root_directory), fname)
    shutil.copy2(_from, _to)
    return _to

def _durl(root_directory, form_value, val):
    """
    Download the file(s) form url.
    """
    debug('fetch from url')
    
    fname, val = take_filename_and_path(val)
    _to = os.path.join(temporary_directory(root_directory), fname)
    download_from_url(val, _to)
    return _to

def download_file_field(ff, to):
    """
    :param ff : the file field
    :param to : the path to write the file field
    :return to
    """
    with open(to, 'w') as tmp_file:
        tmp_file.write(ff.value)
    return to


def take_filename_and_path(value):
    try:
        # file come from a registered service
        loaded = json.loads(value)
        fname = loaded['n']
        path = loaded['p']
        print fname, path
        return fname, path
    except (ValueError, KeyError, TypeError):
        # so this is an url an we have to guess the name from it.
        # we take the last pasrt of the URL
        lastpart = os.path.split(value)[1]
        try:
            fname = NAME_PATTERN.search(lastpart).group('name')
            try:
                ftype = HTS_TYPE_PATTERN.search(lastpart).group('type')
                # the file comme from HTS and we succeed taking fname & ftype from the URL
                return '%s.%s' % (fname, ftype), value
            except AttributeError:
                # the ftype is not in the url, so the file is not from HTS, we can assume
                # that the fname will also contains the extension
                return fname, value

        except AttributeError:
            # the file name is not in a parameter so we take the last part of the url
            # minus the parameters
            return lastpart.split('?')[0], value


def download_from_url(_from, _to):
        u = urlparse.urlparse(_from)
        if not u.hostname:
            raise UrlError('"%s" is not a valid URL.' % _from)
        try:
            u = urllib2.urlopen(_from)
            with open(_to, 'w') as out:
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break
                    out.write(buffer)
            return True
        except urllib2.HTTPError as e:
            print '%s : %s' % (_from, e)
            raise e


class FileChunk(object):

    chunk_size = 4096

    def __init__(self, filename, length, start=None, stop=None):
        self.filename = filename
        self.start = start
        self.stop = stop
        self.len = length

    def read(self):
        self.fileobj = open(self.filename, 'rb')
        if self.start:
            self.fileobj.seek(self.start)
        if self.stop:
            sz = self.stop - self.start
            return self.fileobj.read(sz)
        return self.fileobj.read()
