from bs.lib import base
from tg import expose, response, url
from bs.model import DBSession, Job, Result, PluginRequest
import os
from datetime import datetime
from sqlalchemy.sql import expression


class JobController(base.BaseController):

    @expose('mako:bs.templates.job_index')
    def index(self, task_id=None):
        if task_id is None:
            return {'job_id': None}
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return {'job_id': True, 'error': 'Wrong job identifier, "%s" is not recognized as a valid job.' % task_id}
        results = [{'is_file': result.is_file, 'result': result.result, 'path':get_result_url(result, task_id), 'fname': result.fname} for result in job.results]

        # additionnal information
        trace = job.error or ''
        req = job.request
        plug = req.plugin
        datedone = datetime.strftime(req.date_done, '%a %d %b %Y at %H:%M:%S')
        plugin_id = plug.id
        plugin_info = plug.info
        parameters = req.parameters

        return {'status': job.status, 'task_id': task_id, 'job_id': job.id, 'results': results,
        'traceback': trace, 'date': datedone, 'plugin_id': plugin_id, 'plugin_info': plugin_info,
         'parameters': parameters}

    @expose('mako:bs.templates.job_all')
    def all(self):
        jobs = DBSession.query(Job).join(PluginRequest).order_by(expression.desc(PluginRequest.date_done)).all()
        return {'jobs': jobs}

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

    @expose('json')
    def info(self, task_id):
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        req = job.request
        results = [{'id': r.id, 'result': r.result, 'is_file': r.is_file, 'fname': r.fname} for r in job.results]
        return {'results': results, 'status': job.status, 'plugin_id': req.plugin.id, 'parameters': req.parameters}


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
