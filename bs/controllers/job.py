from bs.lib import base
from tg import expose, response, url, request
from bs.model import DBSession, Job, PluginRequest
import os
from datetime import datetime
from sqlalchemy.sql import expression
from bs.lib import filemanager


class JobController(base.BaseController):

    @expose('mako:bs.templates.job_index')
    def index(self, task_id=None):
        if task_id is None:
            return {'job_id': None}
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return {'job_id': True, 'error': 'Wrong job identifier, "%s" is not recognized as a valid job.' % task_id}
        results = [{'is_file': result.is_file,
                    'result': result.result,
                    'path': get_result_url(result, task_id),
                    'fname': result.fname} for result in job.results]

        # additionnal information
        trace = job.simple_error or ''
        complete = job.error or ''
        req = job.request
        plug = req.plugin
        datedone = datetime.strftime(req.date_done, '%a %d %b %Y at %H:%M:%S')
        plugin_id = plug.id
        plugin_info = plug.info
        parameters = req.parameters

        return {'status': job.status,
                'task_id': task_id,
                'job_id': job.id,
                'results': results,
                'traceback': trace,
                'full_traceback': complete,
                'date': datedone,
                'plugin_id': plugin_id,
                'plugin_info': plugin_info,
                'parameters': parameters}

    @expose('mako:bs.templates.job_all')
    def all(self, limit=None):
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                pass
        limit = (limit or 50)
        jobs = DBSession.query(Job).join(PluginRequest).order_by(expression.desc(PluginRequest.date_done))[:limit]
        return {'jobs': jobs}

    @expose(content_type='toto/tata')
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
    ext = os.path.splitext(fname)[1].lower()

    sz = os.path.getsize(file_path)
    lm = os.path.getmtime(file_path)
    lm = datetime.fromtimestamp(lm).strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.content_length = '%s' % sz
    if ext in ['.pdf', '.gz', '.gzip']:
        response.content_type = 'application/' + ext
    elif ext in ['.png', '.jpeg', '.jpg', '.gif']:
        response.content_type = 'image/' + ext
    elif ext in ['.sql', '.db', '.sqlite3']:
        response.content_type = 'application/x-sqlite3'
    elif ext in ['.bw', '.bigw', '.bigwig']:
        response.content_type = 'application/octet-stream'
    else:
        response.content_type = "text/plain"
    octet_size = sz / 8
    if not octet_size:
        octet_size = 1
    response.headers['Content-Disposition'] = 'attachement; filename=%s; size=%s' % (fname, sz)
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = '%s' % octet_size
    response.headers['Last-Modified'] = lm
    response.headers['Content-Description'] = "Bioscript result"
    response.etag = '%s' % hash(file_path)
    start = stop = None
    if request.range:
        try:
            start, stop = str(request.range).split('=')[-1].split('-')
            start = int(start)
            stop = int(stop)
            if stop == start:
                stop += 1
            if stop > sz:
                stop = sz - 1
            newsz = stop - start
            response.headers["Content-Range"] = "bytes %s-%s/%s" % (start, stop, sz)
            response.headers['Content-Disposition'] = 'attachement; filename=%s; size=%s' % (fname, newsz)
            response.content_length = '%s' % (newsz)
        except ValueError:
            pass
    print response.headers
    fiter = filemanager.FileIterable(file_path, start, stop)
    return fiter
