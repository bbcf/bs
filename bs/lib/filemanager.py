from bs.operations import wordlist
from bs.lib import constants, services
import tempfile
import os
import shutil
import urlparse
import urllib2

block_sz = 2048 * 4


DEBUG_LEVEL = 0


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[filemanager] %s%s' % ('\t' * t, s)


def temporary_directory(directory=None):
    return tempfile.mkdtemp(dir=directory)


def fetch(user, plugin, form_parameters):
    """
    Fetch file from a plugin form and update form_parameters.
    :param form_parameters: the form parameters
    TODO : it's not elegent cause of multiple refactoring but it's working
    """
    file_ids = [file_parameter.get('id') for file_parameter in plugin.in_params_typeof(wordlist.FILE)]
    debug(form_parameters)
    root_directory = temporary_directory(constants.paths['tmp'])
    debug('FETCH')
    for fid in file_ids:
        form_value = form_parameters.get(fid, None)
        if form_value is None:
            # it can be a multi - upload so we regroup all parameters starting with `fid`
            # under `fid` parameter
            files = []
            todel = []
            for k, v in form_parameters.iteritems():
                if k.startswith('%s:' % fid):
                    files.append(v)
                    todel.append(k)
            for k in todel:
                del form_parameters[k]
            form_value = files
        debug("download '%s' ? " % fid, 1)
        debug(form_value)
        debug(type(form_value))
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

            if not isinstance(test, basestring):
                    is_file_field = True
                    debug('file field', 3)

            # download file field(s)
            if is_file_field:
                if is_list:
                    input_files = [download_file_field(v, os.path.join(temporary_directory(root_directory), v.filename)) for v in form_value]
                else:
                    input_files = [download_file_field(form_value, os.path.join(temporary_directory(root_directory), form_value.filename))]

            # download url(s)
            else:
                # take file from filesystem because these are fakes urls
                if user.is_service:
                    debug('is service', 2)
                    file_root = services.service_manager.get(user.name, constants.SERVICE_FILE_ROOT_PARAMETER)
                    debug('got file_root : %s' % file_root, 4)
                    url_root = services.service_manager.get(user.name, constants.SERVICE_URL_ROOT_PARAMETER)
                    debug('got url_root : %s' % url_root, 4)

                    if is_list:
                        input_files = []
                        for fvalue in form_value:
                            fvalue = fvalue.replace('//', '/').replace(':/', '://')
                            _from = fvalue.replace(url_root, file_root)
                            _to = os.path.join(temporary_directory(root_directory), os.path.split(file_root)[1])
                            shutil.copy2(_from, _to)
                            input_files.append(_to)
                    else:
                        # remove //. Servide defined a directory where to take & put files
                        # so the urls are fakes
                        form_value = form_value.replace('//', '/').replace(':/', '://')
                        _from = form_value.replace(url_root, file_root)
                        _to = os.path.join(temporary_directory(root_directory), os.path.split(file_root)[1])
                        shutil.copy2(_from, _to)
                        input_files = [_to]

                # take files from urls
                else:
                    debug('is user', 2)
                    if is_list:
                        input_files = []
                        for fvalue in form_value:
                            _to = os.path.join(temporary_directory(root_directory), os.path.split(fvalue)[1].split('?')[0])
                            download_from_url(fvalue, _to)
                            input_files.append(_to)
                    else:
                        _to = os.path.join(temporary_directory(root_directory), os.path.split(form_value)[1].split('?')[0])
                        download_from_url(form_value, _to)
                        input_files = [_to]

            if len(input_files) == 1:
                input_files = input_files[0]
        else:
            input_files = ''

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


def download_from_url(_from, _to):
        u = urlparse.urlparse(_from)
        if not u.hostname:
            raise urllib2.HTTPError('%s is not a valid URL.' % _from)
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
