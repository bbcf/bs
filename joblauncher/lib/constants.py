from pkg_resources import resource_filename
import os

tmp_user_name = 'tmp_user'

group_admins_id = 1
group_admins_name = 'Admins'
group_users_id = 2
group_users_name = 'Users'

permission_admin_name = 'admin'
permission_admin_desc = 'This permission give admin right to the bearer'
permissions_read_name = 'read'
permission_read_desc = 'This permission give "read" right to the bearer'

REQUEST_TYPE = 'REQUEST_CLASSIFIER'
REQUEST_TYPE_COMMAND_LINE = 'command_line'
REQUEST_TYPE_BROWSER = 'browser'


def plugin_directory():
    return os.path.join(resource_filename('joblauncher', 'plugins'))