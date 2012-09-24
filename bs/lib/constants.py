from pkg_resources import resource_filename
import os, tg

tmp_user_name = 'tmp_user'

group_admins_id = 1
group_admins_name = 'Admins'
group_users_id = 2
group_users_name = 'Users'
group_services_id = 3
group_services_name = 'Services'

permission_admin_name = 'admin'
permission_admin_desc = 'This permission give admin right to the bearer'
permissions_read_name = 'read'
permission_read_desc = 'This permission give "read" right to the bearer'

REQUEST_TYPE = 'REQUEST_CLASSIFIER'
REQUEST_TYPE_SERVICE = 'service'
REQUEST_TYPE_BROWSER = 'browser'


SERVICE_SHARED_KEY = 'shared_key'
SERVICE_HTTP_REFERER = 'http.referer'
SERVICE_FILE_ROOT_PARAMETER = 'file.root'
SERVICE_URL_ROOT_PARAMETER = 'url.root'
SERVICE_RESULT_ROOT_PARAMETER = 'result.root'
SERVICE_CALLBACK_URL_PARAMETER = 'callback.url'

date_format = "%d. %b %Y %Hh%M"

def plugin_directory():
    return os.path.join(resource_filename('bs', 'operations'), 'plugins')

def services_directory():
    return os.path.normpath(os.path.join(resource_filename('bs', os.path.pardir), 'services.ini'))

def services_config_file():
    return os.path.normpath(os.path.join(resource_filename('bs', os.path.pardir), 'services.cfg'))


def service_name(service):
    return 'service_%s_jl' % service

def decypher_service_name(service):
    return service[8:-3]


def service_email(service):
    return 'service_%s' % service


def temporary_directory():
    if 'temporary.directory' in tg.config:
        return tg.config.get('temporary.directory')
    else :
        return os.path.join(resource_filename('bs', 'tmp'))
