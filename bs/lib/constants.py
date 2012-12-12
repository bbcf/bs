from pkg_resources import resource_filename
import os
import tg
from bs import PROJECT_ROOT

SERVICE_SHARED_KEY = 'shared_key'
SERVICE_HTTP_REFERER = 'http.referer'
SERVICE_FILE_ROOT_PARAMETER = 'file.root'
SERVICE_URL_ROOT_PARAMETER = 'url.root'
SERVICE_RESULT_ROOT_PARAMETER = 'result.root'
SERVICE_CALLBACK_URL_PARAMETER = 'callback.url'

date_format = "%d. %b %Y %Hh%M"


paths = {
    'plugins': os.path.join(PROJECT_ROOT, 'operations', 'plugins'),
    'services': os.path.normpath(os.path.join(PROJECT_ROOT, os.path.pardir, 'services.ini')),
    'tmp': os.path.normpath(os.path.join(PROJECT_ROOT, 'tmp')),
    'data': os.path.normpath(os.path.join(PROJECT_ROOT, 'bioscript_data'))
}

files = {
    'services': {
        'ini': os.path.normpath(os.path.join(PROJECT_ROOT, os.path.pardir, 'services.ini')),
        'cfg': os.path.normpath(os.path.join(PROJECT_ROOT, os.path.pardir, 'services.cfg')),
    }
}

def plugin_directory():
    return paths['plugins']


def services_directory():
    return files['services']['ini']


def services_config_file():
    return files['services']['cfg']


def service_name(service):
    return 'service_%s_jl' % service


def decypher_service_name(service):
    return service[8:-3]


def service_email(service):
    return 'service_%s' % service


def temporary_directory():
    if 'temporary.directory' in tg.config:
        return tg.config.get('temporary.directory')
    else:
        return os.path.join(resource_filename('bs', 'tmp'))
