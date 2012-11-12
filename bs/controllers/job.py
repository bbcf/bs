from bs.lib import base
from tg import expose, response, url
from bs.model import DBSession, Job, Result
import os


class JobController(base.BaseController):

    @expose('mako:bs.templates.job_index')
    def index(self, task_id=None):
        if task_id is None:
            return {'job_id': None}
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return {'job_id': True, 'error': 'Wrong job identifier, "%s" is not recognized as a valid job.' % task_id}
        results = [{'is_file': result.is_file, 'result': result.result, 'path':get_result_url(result, task_id), 'fname': result.fname} for result in job.results]
        return {'status': job.status, 'task_id': task_id, 'job_id': job.id, 'results': results}

    @expose('mako:bs.templates.job_result')
    def get(self, task_id, result_id):
        result_id = int(result_id)
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        for result in job.results:
            if result.id == result_id:
                if result.is_file:
                    return file_response(result.path)
                else:
                    return {'result': result.result}
        return {'error': "Job identifier & result identifier doesn't correspond."}


def get_result_url(result, task_id):
    if not result.is_file:
        return ''
    return url('jobs/get', {'task_id': task_id, 'result_id': result.id})


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
