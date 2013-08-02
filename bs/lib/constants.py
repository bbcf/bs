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

ROOT_DIRECTORY = tg.config.get('root.directory')
FROMCELERY = False

if not ROOT_DIRECTORY:
    from celery import current_app
    if 'ROOT_DIRECTORY' in current_app.conf:
        ROOT_DIRECTORY = current_app.conf['ROOT_DIRECTORY']
    else :
        raise Exception('You must set ROOT_DIRECTORY parameter in celery configuration file')
    FROMCELERY = True



paths = {
    'plugins': os.path.join(PROJECT_ROOT, 'operations', 'plugins'),
    'services': os.path.normpath(os.path.join(ROOT_DIRECTORY, os.path.pardir, 'services.ini')),
    'tmp': os.path.normpath(os.path.join(ROOT_DIRECTORY, 'tmp')),
    'data': os.path.normpath(os.path.join(ROOT_DIRECTORY, 'bioscript_data'))
}

files = {
    'services': {
        'ini': os.path.normpath(os.path.join(ROOT_DIRECTORY, os.path.pardir, 'services.ini')),
        'cfg': os.path.normpath(os.path.join(ROOT_DIRECTORY, os.path.pardir, 'services.cfg')),
    }
}


def check_data_paths():
    if not os.path.exists(ROOT_DIRECTORY):
        print "Directory '%s' does not exist: trying to create it..." % ROOT_DIRECTORY
        os.mkdir(ROOT_DIRECTORY)
        print 'ok'
    if not os.path.exists(paths['tmp']):
        print "Directory '%s' does not exist: trying to create it..." % paths['tmp']
        os.mkdir(paths['tmp'])
        print 'ok'
    if not os.path.exists(paths['data']):
        print "Directory '%s' does not exist: trying to create it..." % paths['data']
        os.mkdir(paths['data'])
        print 'ok'
    if not os.path.exists(paths['services']):
        raise IOError('You must define the service.ini file. It must be located at %s' % paths['services'])

if not FROMCELERY:
    check_data_paths()


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
    return paths['tmp']
