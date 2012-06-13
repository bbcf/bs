from . import service_manager
from joblauncher.lib import constants, io, util
import os, tempfile, errno, urllib2




def fetch_files(service, _files, form_parameters):
    """
    Fetch the file given in parameter.
    The files are stored in _files parameters but only those
    specified in the form_parameters.
    This update the form_parameters with the new value
    """
    service_name = service.name
    parameters = service_manager.get(service_name)

    file_root = parameters.get(constants.SERVICE_FILE_ROOT_PARAMETER, None)
    url_root = parameters.get(constants.SERVICE_URL_ROOT_PARAMETER, None)

    tmp_dir = temporary_directory(service_name)
    try :
        for form_parameter in _files.keys():
            if form_parameters.has_key(form_parameter):
                value = form_parameters.get(form_parameter)
                tmp_file = util.temporary_path(value, dir=tmp_dir)

                if file_root is not None and url_root is not None:
                    # remove //
                    value = value.replace('//', '/').replace(':/', '://')
                    new = value.replace(url_root, file_root)
                    io.copy(new, tmp_file)
                else :
                    io.download(value, tmp_file)
                form_parameters[form_parameter] = tmp_file
    except IOError as e:
        io.rm(tmp_dir)
        raise e
    return tmp_dir

def fetch_file_field(user, _files, form_parameters):
    tmp_dir = temporary_directory(user.name)
    try :
        for form_parameter in _files:
            if form_parameters.has_key(form_parameter):
                value = form_parameters.get(form_parameter)
                filename = value.filename
                file_value = value.value
                tmp_file = util.temporary_path(filename, dir=tmp_dir)
                with open (tmp_file, 'w') as _f:
                    _f.write(file_value)
                form_parameters[form_parameter] = tmp_file
    except IOError as e:
        io.rm(tmp_dir)
        raise e
    return tmp_dir

def out_path(service_name):
    parameters = service_manager.get(service_name)
    out = parameters.get(constants.SERVICE_RESULT_ROOT_PARAMETER, False)
    if not out:
        out = service_manager.out_path
    return out




def temporary_path(service_name, extension=None, filename='in'):
    """
    Build a temporary path in a temporary directory
    """
    unique = util.id_generator()
    tmp_dir = os.path.join(service_manager.in_path, service_name, unique)
    try:
        os.mkdir(tmp_dir)
    except OSError, e:
        if e.errno == errno.EEXIST:
            return temporary_path(service_name, extension, filename)
        else: #this error must be raised to tell that something wrong with mkdir
            raise OSError

    unique_path = os.path.join(tmp_dir, filename)
    if extension is not None:
        return '%s.%s' % (unique_path, extension)
    return tmp_dir, unique_path

def temporary_directory(service_name=None):
    """
    Build a temporary directory in the service directory
    """
    if service_name is None :
        tmp_dir = util.temporary_path(dir=service_manager.in_path)
    else :
        tmp_dir = util.temporary_path(dir=os.path.join(service_manager.in_path, service_name))
    return tmp_dir