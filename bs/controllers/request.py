from bs.lib import constants, base, util
from repoze.what.predicates import has_permission
from tg import request, expose, url, flash, redirect, response
from bs.widgets.request import request_list, request_object
#from bs.model import DBSession, Request, Result, Task
import os


class RequestController(base.BaseController):
    pass


    # @expose('mako:bs.templates.request_index')
    # def index(self, task_id, **kw):
    #     req_data = DBSession.query(Request).join(Result).filter(Result.task_id == task_id).first()
    #     if req_data is None:
    #         return {'status' : 'FAILURE', 'msg' : 'Wrong task identifier.'}

    #     if req_data.result.task is None: status = 'PENDING'
    #     else :                           status = req_data.result.task.status

    #     if status == 'FAILURE':
    #         return {'status' : status, 'msg' : req_data.result.task.traceback}
    #     elif status == 'PENDING':
    #         return {'status' : status, 'msg' : 'Processing still running.'}

    #     elif status == 'SUCCESS':

    #         out = os.path.join(req_data.result.path, task_id)
    #         print out

    #         results = os.listdir(out)
    #         print results
    #         if len(results) == 0:
    #             return {'status' : 'NORESULT', 'msg' : 'no results'}
    #         name = kw.get('name', None)
    #         if len(results) == 1:
    #             name = results[0]
    #             print name

    #         if name is not None and name in results:
    #             ext = os.path.splitext(name)[1]
    #             if ext.lower() in ['.pdf', '.gz', '.gzip']:
    #                 response.content_type = 'application/' + ext.lower()
    #             elif ext.lower() in ['.png', '.jpeg', '.jpg', '.gif']:
    #                 response.content_type = 'image/' + ext.lower()
    #             elif ext.lower() in ['.sql', '.db', '.sqlite3']:
    #                 response.content_type = 'application/x-sqlite3'
    #             else :
    #                 response.content_type = "text/plain"
    #             out_file = os.path.normpath(os.path.join(out, name))
    #             if not out_file.startswith(out):
    #                 return "Are you kidding me?"
    #             response.headerlist.append(('Content-Disposition', 'attachment;filename="%s"' % name))
    #             return open(out_file).read()

    #         return {'status' : status, 'results' : results, 'links' : url('/requests', {'task_id' : task_id})}




    # @expose('json')
    # def status(self, task_id):
    #     t = DBSession.query(Task).filter(Task.task_id == task_id).first()
    #     if t is None:
    #         return {'status' : 'PENDING'}
    #     return {'status' : t.status}

    # @expose('json')
    # def get(self, task_id):
    #     req_data = DBSession.query(Request).join(Result).filter(Result.task_id == task_id).first()
    #     return {'result' : request_object(req_data)}

    # @expose('bs.templates.results')
    # def result(self, task_id, name=None):
    #     req_data = DBSession.query(Request).join(Result).filter(Result.task_id == task_id).first()

    #     if not req_data:
    #         flash('wrong task identifier : %s' % task_id, 'error')
    #         raise redirect(url("/"))

    #     if req_data.result.task is None: status = 'PENDING'
    #     else :                           status = req_data.result.task.status
    #     if status == 'SUCCESS':

    #         out = os.path.join(req_data.result.path, task_id)
    #         print out

    #         results = os.listdir(out)
    #         print results
    #         if len(results) == 0:
    #             return 'no result'

    #         if len(results) == 1:
    #             name = results[0]

    #         if name is not None and name in results:
    #             ext = os.path.splitext(name)[1]
    #             if ext.lower() in ['.pdf', '.gz', '.gzip']:
    #                 response.content_type = 'application/' + ext.lower()
    #             elif ext.lower() in ['.png', '.jpeg', '.jpg', '.gif']:
    #                 response.content_type = 'image/' + ext.lower()
    #             elif ext.lower() in ['.sql', '.db', '.sqlite3']:
    #                 response.content_type = 'application/x-sqlite3'
    #             else :
    #                 response.content_type = "text/plain"
    #             out_file = os.path.normpath(os.path.join(out, name))
    #             if not out_file.startswith(out):
    #                 return "Are you kidding me?"
    #             response.headerlist.append(('Content-Disposition', 'attachment;filename=%s' % results[0]))
    #             return open(out_file).read()

    #         return {'page' : 'request', 'results' : results, 'linkto' : url('/requests/result', {'task_id' : task_id})}

    #     elif status == 'FAILURE':
    #         return req_data.result.task.traceback

    #     return "Data being processed"


