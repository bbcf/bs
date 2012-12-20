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
    """
    file_ids = [file_parameter.get('id') for file_parameter in plugin.in_params_typeof(wordlist.FILE)]
    debug(form_parameters)
    root_directory = temporary_directory(constants.paths['tmp'])
    debug('FETCH')
    for fid in file_ids:
        form_value = form_parameters.get(fid, None)
        debug("download '%s' ? " % fid, 1)
        if form_value is not None:
            if not isinstance(form_value, basestring):  # its a file field
                debug('file field', 3)
                if isinstance(form_value, (list, tuple)):
                    debug('is list', 3)
                    input_files = [download_file_field(v, os.path.join(temporary_directory(root_directory), v.filename)) for v in form_value]
                else:
                    input_files = [download_file_field(form_value, os.path.join(temporary_directory(root_directory), form_value.filename))]
            else:
                if user.is_service:
                    debug('is service', 2)
                    file_root = services.service_manager.get(user.name, constants.SERVICE_FILE_ROOT_PARAMETER)
                    debug('got file_root : %s' % file_root, 4)
                    url_root = services.service_manager.get(user.name, constants.SERVICE_URL_ROOT_PARAMETER)
                    debug('got url_root : %s' % url_root, 4)
                    # remove //. Servide defined a directory where to take & put files
                    # so the urls are fakes
                    form_value = form_value.replace('//', '/').replace(':/', '://')
                    _from = form_value.replace(url_root, file_root)
                    _to = os.path.join(temporary_directory(root_directory), os.path.split(file_root)[1])
                    shutil.copy2(_from, _to)
                    input_files = [_to]

                else:
                    debug('url from user', 2)
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
