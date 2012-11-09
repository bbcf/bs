from bs.lib import constants, base, util
from repoze.what.predicates import has_permission
from tg import request, expose, url, flash, redirect, response
from bs.widgets.request import request_list, request_object
from bs.model import DBSession, Job, Result, Job
import os


class JobController(base.BaseController):

    @expose('mako:bs.templates.job_index')
    def index(self, task_id=None):
        if task_id is None:
            return {'job_id': None}
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return {'job_id': True, 'error': 'Wrong job identifier, "%s" is not recognized as a valid job.' % task_id}
        return {'job_id': job.id, 'results': job.results}

    @expose('mako:bs.templates.job_result')
    def get(self, task_id, result_id):
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        for result in job.results:
            if result.id == result_id:
                if result.is_file:
                    return file_response(result.path)
                else:
                    return {'result': result.result}

        return {'error': "Job identifier & result identifier doesn't correspond"}


def file_response(file_path):
    fname = os.path.split(file_path)[1]
    ext = os.path.splitext(fname)[1]
    if ext.lower() in ['.pdf', '.gz', '.gzip']:
        response.content_type = 'application/' + ext.lower()
    elif ext.lower() in ['.png', '.jpeg', '.jpg', '.gif']:
        response.content_type = 'image/' + ext.lower()
    elif ext.lower() in ['.sql', '.db', '.sqlite3']:
        response.content_type = 'application/x-sqlite3'
    else:
        response.content_type = "text/plain"
    response.headerlist.append(('Content-Disposition', 'attachment;filename="%s"' % fname))
    return open(file_path).read()
