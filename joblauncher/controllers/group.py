"""Group Controller"""

from tgext.crud import CrudRestController
from tg import expose, flash
from repoze.what.predicates import has_permission
from tg.controllers import redirect
from joblauncher.widgets.group import group_table, group_table_filler, new_group_form, group_edit_filler, group_edit_form
from joblauncher.model import DBSession, Group
from joblauncher.lib import constants

__all__ = ['GroupController']



class GroupController(CrudRestController):
    allow_only = has_permission(constants.permission_admin_name)
    model = Group
    table = group_table
    table_filler = group_table_filler
    edit_form = group_edit_form
    new_form = new_group_form
    edit_filler = group_edit_filler

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        for id in args :
            group = DBSession.query(Group).filter(Group.id == id).first()
            if group.id == constants.group_admins_id:
                flash('Cannot delete admin group', 'error')
                redirect('/groups')
            if group.name == constants.group_users_id:
                flash('Cannot delete users group', 'error')
                redirect('/groups')
        return CrudRestController.post_delete(self, *args, **kw)