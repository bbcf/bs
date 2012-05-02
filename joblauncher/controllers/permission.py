"""Permission Controller"""

from tgext.crud import CrudRestController



from repoze.what.predicates import has_permission



from tg import expose, flash

from tg.controllers import redirect

from joblauncher.lib import constants

from joblauncher.widgets.permission import perm_table, perm_table_filler, perm_new_form, perm_edit_filler, perm_edit_form

from joblauncher.model import DBSession, Permission



class PermissionController(CrudRestController):

    allow_only = has_permission(constants.permission_admin_name)
    model = Permission
    table = perm_table
    table_filler = perm_table_filler
    edit_form = perm_edit_form
    new_form = perm_new_form
    edit_filler = perm_edit_filler





    @expose('genshi:tgext.crud.templates.post_delete')

    def post_delete(self, *args, **kw):
        for id in args :
            permission = DBSession.query(Permission).filter(Permission.id == id).first()
            if permission.id == constants.permission_admin_name:
                flash('Cannot delete admin permission', 'error')
                redirect('/permissions')
            if permission.name == constants.permissions_read_name:
                flash('Cannot delete read permission', 'error')
                redirect('/permissions')
        return CrudRestController.post_delete(self, *args, **kw)
