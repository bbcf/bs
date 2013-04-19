from bs.lib.operations import wordlist
from bs.lib import constants, services
import tempfile
import os
import shutil
import urlparse
import urllib2
import json

block_sz = 2048 * 4


DEBUG_LEVEL = 0


class UrlError(Exception):
    pass


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[filemanager] %s%s' % ('\t' * t, s)


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


def fetch(user, plugin, form_parameters):
    """
    Fetch file from a plugin form and update form_parameters.
    :param form_parameters: the form parameters
    TODO : it's not elegent cause of multiple refactoring but it's working
    """
    files = plugin.in_params_typeof(wordlist.FILE)
    #regoup_multiple_field_in_list(form_parameters)

    root_directory = temporary_directory()
    debug('FETCH %s' % form_parameters)
    for infile in files:
        debug("download '%s' ? " % infile, 1)
        fid = infile.get('id')
        form_value = None
        if infile.get('multiple', False):
            debug('is multiple', 2)
            form_value = form_parameters.get(infile['multiple'], {}).get(fid, None)
        else:
            form_value = form_parameters.get(fid, None)
        debug(form_value)
        # check if form_value contains a value or is not an empty list
        if form_value is not None and (not isinstance(form_value, (list, tuple)) or len(form_value) > 0) and form_value != '':
            # check if we have file fields or urls
            is_file_field = False
            is_list = False
            test = form_value
            if isinstance(form_value, (list, tuple)):
                is_list = True
                debug('is list', 3)
                test = form_value[0]
            debug('testing %s of type %s' % (test, type(test)), 3)
            if not isinstance(test, basestring):
                    is_file_field = True
                    debug('is file field', 3)

            # download FILE FIELD
            if is_file_field:
                if is_list:
                    input_files = [download_file_field(v, os.path.join(temporary_directory(root_directory), v.filename)) for v in form_value]
                else:
                    input_files = [download_file_field(form_value, os.path.join(temporary_directory(root_directory), form_value.filename))]

            # download URL
            else:
                # fake urls
                input_files = []
                if user.is_service:
                    debug('is service', 2)
                    file_root = services.service_manager.get(user.name, constants.SERVICE_FILE_ROOT_PARAMETER)
                    debug('got file_root : %s' % file_root, 4)
                    url_root = services.service_manager.get(user.name, constants.SERVICE_URL_ROOT_PARAMETER)
                    debug('got url_root : %s' % url_root, 4)

                    if is_list:
                        for fvalue in form_value:
                            fname, fvalue = take_filename_and_path(fvalue)
                            fvalue = fvalue.replace('//', '/').replace(':/', '://')
                            _from = fvalue.replace(url_root, file_root)
                            _to = os.path.join(temporary_directory(root_directory), fname)
                            shutil.copy2(_from, _to)
                            input_files.append(_to)
                    else:
                        # remove //. Servide defined a directory where to take & put files
                        # so the urls are fakes
                        fname, fvalue = take_filename_and_path(form_value)
                        fvalue = fvalue.replace('//', '/').replace(':/', '://')
                        _from = fvalue.replace(url_root, file_root)
                        _to = os.path.join(temporary_directory(root_directory), fname)
                        shutil.copy2(_from, _to)
                        input_files.append(_to)

                # real urls
                else:
                    debug('is user', 2)
                    if is_list:
                        for fvalue in form_value:
                            fname, fvalue = take_filename_and_path(fvalue)
                            _to = os.path.join(temporary_directory(root_directory), fname)
                            download_from_url(fvalue, _to)
                            input_files.append(_to)
                    else:
                        _to = os.path.join(temporary_directory(root_directory), os.path.split(form_value)[1].split('?')[0])
                        download_from_url(form_value, _to)
                        input_files.append(_to)

            if len(input_files) == 1:
                input_files = input_files[0]
        else:
            input_files = ''

        # Update parameters
        if infile.get('multiple', False):
            form_parameters[infile.get('multiple')] = {fid: input_files}
        else:
            form_parameters[fid] = input_files
        debug(form_parameters)
    return root_directory


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
        loaded = json.loads(value)
        fname = loaded['n']
        path = loaded['p']
        return fname, path
    except ValueError, KeyError:
        return os.path.split(value)[1].split('?')[0], value


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


class FileIterable(object):

    def __init__(self, filename, start=None, stop=None):
        self.filename = filename
        self.start = start
        self.stop = stop

    def __iter__(self):
        return FileIterator(self.filename, self.start, self.stop)

    def app_iter_range(self, start, stop):
        return self.__class__(self.filename, start, stop)

    

class FileIterator(object):
    chunk_size = 4096

    def __init__(self, filename, start, stop):
        self.filename = filename
        self.fileobj = open(self.filename, 'rb')
        if start:
            self.fileobj.seek(start)
        if stop is not None:
            self.length = stop - start
        else:
            self.length = None

    def __iter__(self):
        return self

    def next(self):
        if self.length is not None and self.length <= 0:
            raise StopIteration
        chunk = self.fileobj.read(self.chunk_size)
        if not chunk:
            raise StopIteration
        if self.length is not None:
            self.length -= len(chunk)
            if self.length < 0:
                # Chop off the extra:
                chunk = chunk[:self.length]
        return chunk
    __next__ = next  # py3 compat


def get_mimetype(filename):
    import mimetypes
    _type, encoding = mimetypes.guess_type(filename)
    # We'll ignore encoding, even though we shouldn't really
    return _type or 'application/octet-stream'


def serve_file(response, filename, start=None, stop=None):
    response.app_iter = FileIterable(filename, start, stop)
    response.content_length = os.path.getsize(filename)
    response.last_modified = os.path.getmtime(filename)
    response.etag = '%s-%s-%s' % (os.path.getmtime(filename),
                                  os.path.getsize(filename), hash(filename))
    return response
