from . import service_manager
from joblauncher.lib import constants, io, util
import os


def fetch_file(service, param, value, extension=None):
    """
    Fetch the file from the service and copy it in joblauncher.
    param: service - the name of the service
    param: param - the path where to fetch the file
    Return: the path where the file is copied.
    """
    service_name = constants.decypher_service_name(service.name)
    parameters = service_manager.get(service_name)
    out = temporary_path(service_name, extension)
    file_root = parameters.get(constants.SERVICE_FILE_ROOT_PARAMETER, None)
    url_root = parameters.get(constants.SERVICE_URL_ROOT_PARAMETER, None)
    print out
    try :

    if file_root is not None and url_root is not None:
        new = value.replace(url_root, file_root)
        io.copy(new, out)
    else :
        io.download(value, out)
    except Exception as e:
        io.rm(out)
    return out




def temporary_path(service_name, extension=None, filename='in'):
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
    return unique_path