from joblauncher.lib import constants, base, util
from repoze.what.predicates import has_permission
from tg import request, expose, url, flash
from joblauncher.widgets.request import request_list, request_object
from joblauncher.model import DBSession, Request, Result, Task



class RequestController(base.BaseController):
    allow_only = has_permission(constants.permission_admin_name)


    @expose('joblauncher.templates.request')
    def index(self):
        req_data = DBSession.query(Request).all()
        dg = util.to_datagrid(request_list, req_data, "Requests", len(req_data)>0)
        return {'page' : 'requests', 'request_list' : [dg]}


    @expose('json')
    def status(self, task_id):
        t = DBSession.query(Task).filter(Task.task_id == task_id).first()
        return {'status' : t.status}

    @expose('json')
    def get(self, task_id):
        req_data = DBSession.query(Request).join(Result).filter(Result.task_id == task_id).first()
        print req_data
        return {'result' : request_object(req_data)}
