from bs.lib import base, operations
from tg import expose, response, url, request
from sqlalchemy.sql.expression import desc, asc
from bs.model import DBSession, Job, PluginRequest, Task, User, Plugin
import os
from datetime import datetime, timedelta
from sqlalchemy.sql import expression
from bs.lib import operations, biorepo
from bs.lib import filemanager
try:
    import simplejson as json
except ImportError:
    import json


DAYS_LIMIT = 30

class JobController(base.BaseController):

    @expose('mako:bs.templates.job_index')
    def index(self, task_id=None, forceurl=False):
        if task_id is None:
            return {'job_id': None}
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return {'job_id': True, 'haserror': True, 'error': 'Wrong job identifier, "%s" is not recognized as a valid job.' % task_id,
            'biorepodata': "{}",
            'biorepourl': ''}
        
        if job.task is None:
            return  {'job_id': True, 'haserror': True, 'error': 'Task "%s" is PENDING.' % task_id,
             'biorepodata': "{}",
            'biorepourl': ''}
        req = job.request
        now = datetime.now()
        delta = timedelta(days=DAYS_LIMIT)

        deletion_date = job.task.date_done + delta
        jobdelta = now - job.task.date_done
        biorepodata = {}
        results = []
        print '#############################'
        print job
        print job.results
        for result in job.results:
            uri=''
            if jobdelta > delta and not forceurl:
                d = jobdelta - delta
                mess = 'File "%s" was deleted %s days ago. Files are kept in Bioscript only %s days.' % (result.fname, d.days, DAYS_LIMIT)
                is_url = False
            else:
                d = delta - jobdelta
                uri = request.application_url + '/' + get_result_url(result, task_id)
                is_url = True
                mess = '<b>File will be deleted in %s days</b>.  Files are kept in Bioscript only %s days.' % (d.days, DAYS_LIMIT)
                if biorepo.SERVICE_UP:
                    dt = {
                        'file_path': uri,
                        'description': req.description(),
                        'project_name': 'Bioscript',
                        'sample_name': req.plugin.info.get('title', '-')
                    }
                    biorepodata['brepo_%s' % result.id] = dt
                    mess += ' You could save it in <a id="brepo_%s" class="biorepourl">Biorepo</a>.' % result.id
                ## file_url : uri
                ## desc: req.parameters
                ## project_name: bioscript
                ## sample: plugin.info['title']
            results.append({'is_file': result.is_file,
                'result': result.result,
                'mess': mess,
                'uri': uri,
                'is_url': is_url,
                'fname': result.fname,
                'deletion-date': deletion_date,
                })

        # additionnal information
        trace = job.simple_error or ''
        complete = job.error or ''
        
        plug = req.plugin
        datedone = datetime.strftime(req.date_done, '%a %d %b %Y at %H:%M:%S')
        plugin_id = plug.id
        plugin_info = plug.info
        parameters = req.parameters
        trace = trace.replace('\n', '<br/>')
        complete = complete.replace('\n', '<br/>')
        return {'haserror': False,
                'status': job.status,
                'task_id': task_id,
                'job_id': job.id,
                'results': results,
                'traceback': trace,
                'full_traceback': complete,
                'date': datedone,
                'plugin_id': plugin_id,
                'plugin_info': plugin_info,
                'parameters': parameters,
                'plugin_generated_id': plug.generated_id,
                'biorepodata': json.dumps(biorepodata),
                'biorepourl': biorepo.SERVICE_UP and json.dumps(biorepo.BIOREPO_ACTION_URL) or ''
                }

    @expose('mako:bs.templates.job_all')
    def all(self, limit=None, status=None):
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                pass
        limit = (limit or 50)
        jobs = DBSession.query(Job).join(PluginRequest).order_by(desc(PluginRequest.date_done))[:limit]
        if status and status.lower() in ['success', 'failure', 'started']:
            jobs = [j for j in jobs if j.status == status.upper()]
        return {'jobs': jobs}

    @expose()
    @expose('json')
    @expose('mako:bs.templates.job_result')
    def get(self, task_id, result_id, xsend=False):
        result_id = int(result_id)
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        for result in job.results:
            if result.id == result_id:
                if result.is_file:
                    if xsend:
                        return file_response_with_xsendfile(result.path)
                    return file_response(result.path)
                else:
                    return {'result': result.result}
        return {'error': "Job identifier & result identifier doesn't correspond."}

    @expose('json')
    def info(self, task_id):
        job = DBSession.query(Job).filter(Job.task_id == task_id).first()
        req = job.request
        results = [{'id': r.id, 'result': r.result, 'is_file': r.is_file, 'fname': r.fname} for r in job.results]
        return {'results': results, 'status': job.status, 'plugin_id': req.plugin.id, 'parameters': req.sanitized_parameter()}


    @expose('mako:bs.templates.job_stats')
    def stats(self):
        jobs = DBSession.query(Job).join(PluginRequest).order_by(asc(PluginRequest.date_done)).all()

        # get number of jobs / month, days, ...
        d = {'months' : [0] * 12, 
            'days': [0] * 7,
            'hours': [0] * 24,
            'users': {},
            'remotes': {},
            'plugins': {}
            }
        # set all users to prevent looking if user alrady set for each jobs
        users = DBSession.query(User).all()
        for user in users:
             d['users'][user.name] = 1
             if user.name == 'anonymous':
                d['remotes'][user.remote] = 1
        # do the same for all plugin
        plugs = operations.get_plugins_path(ordered=False)
        for plug in plugs:
            d['plugins'][plug['info']['title']] = 1

        # now look at each jobs one by one
        for job in jobs:
            dd = job.request.date_done.strftime('%m %w %H').split()         
            currentday = int(dd[1])
            d['months'][int(dd[0]) - 1] += 1
            d['days'][currentday] += 1
            d['hours'][int(dd[2])] += 1
            d['users'][job.request.user.name] += 1
            if job.request.user.name == 'anonymous':
                d['remotes'][job.request.user.remote] += 1
            try:
                d['plugins'][job.request.plugin.info['title']] += 1
            except KeyError:
                pass
        d['users'] = [{'name': k, 'value': v} for k, v in d['users'].iteritems()]
        d['remotes'] = [{'name': k, 'value': v} for k, v in d['remotes'].iteritems()]
        return {'jobs': json.dumps(d)}


    @expose('json')
    def statistics(self):
        jobs = DBSession.query(Job).join(PluginRequest).order_by(asc(PluginRequest.date_done)).all()

        # get number of jobs / month, days, ...
        d = {'months' : [0] * 12, 
            'days': [0] * 7,
            'hours': [0] * 24,
            'users': {},
            'plugins': {}
            }
        # set all users to prevent looking if user alrady set for each jobs
        users = DBSession.query(User).all()
        for user in users:
             d['users'][user.name] = 1
        # do the same for all plugin
        plugs = operations.get_plugins_path(ordered=False)
        for plug in plugs:
            d['plugins'][plug['info']['title']] = 1

        # now look at each jobs one by one
        for job in jobs:
            dd = job.request.date_done.strftime('%m %w %H').split()         
            currentday = int(dd[1])
            d['months'][int(dd[0]) - 1] += 1
            d['days'][currentday] += 1
            d['hours'][int(dd[2])] += 1
            d['users'][job.request.user.name] += 1
            try:
                d['plugins'][job.request.plugin.info['title']] += 1
            except KeyError:
                pass
        d['users'] = [{'name': k, 'value': v} for k, v in d['users'].iteritems()]
        return {'jobs': json.dumps(d)}

def serialize_job(job):
    req = job.request
    plugin = req.plugin
    user = req.user
    return {
        'id': job.id,
        'request': {
            'id': req.id,
            'date': {
                'complete': datetime.strftime(req.date_done, '%a %d %b %Y at %H:%M:%S'),
                'hour': datetime.strftime(req.date_done, '%H'),
                'min': datetime.strftime(req.date_done, '%M'),
                'sec': datetime.strftime(req.date_done, '%S'),
                'day': datetime.strftime(req.date_done, '%w'),
                'year': datetime.strftime(req.date_done, '%Y'),
                'month': datetime.strftime(req.date_done, '%m')
            },
            'status': req.status
        },
        'plugin': {
            'id': plugin.id,
            'name': plugin.info['path'][-1]
        },
        'user': {
            'id': user.id,
            'name': user.name,
            'is_service': user.is_service,
            'remote': user.remote
        }
    }


def get_result_url(result, task_id):
    if not result.is_file:
        return ''
    return url('jobs/get', {'task_id': task_id, 'result_id': result.id})


def file_response_with_xsendfile(file_path):
    response.headers['X-Sendfile'] = file_path
    print request
    fname = os.path.split(file_path)[1]
    ext = os.path.splitext(fname)[1].lower()
    response.headers['Content-Disposition'] = 'attachement; filename=%s' % (fname)
    response.headers['Koopa'] = 'troopa'
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
    sz = os.path.getsize(file_path)
    response.content_length = '%s' % (sz)
    return None


def file_response(file_path):
    fname = os.path.split(file_path)[1]
    ext = os.path.splitext(fname)[1].lower()

    sz = os.path.getsize(file_path)
    lm = os.path.getmtime(file_path)
    lm = datetime.fromtimestamp(lm).strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.content_length = sz
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
    # set response headers
    response.headers['Content-Disposition'] = 'attachement; filename=%s; size=%s' % (fname, sz)
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Last-Modified'] = lm
    response.headers['Content-Description'] = "Bioscript result"
    response.headers['Connection'] = "keep-alive"
    response.etag = '%s' % hash(file_path)
    start = stop = None
    totalsize = sz
    if request.range:
        try:
            start, stop = str(request.range).split('=')[-1].split('-')
            start = int(start)
            if stop:
                stop = int(stop)
                if stop == start:
                    stop += 1
                if stop > sz:
                    stop = sz - 1
                sz = stop - start
            else:
                sz -= start
            response.headers["Content-Range"] = "bytes %s-%s/%s" % (start, stop, totalsize)
            response.headers['Content-Disposition'] = 'attachement; filename=%s; size=%s' % (fname, sz)
            response.status = 206
        except ValueError as e:
            print 'Got exception in Range request %s ' % e
            print 'Request-range : %s' % request.range

    response.headers['Content-length'] = '%s' % sz
    fchunk = filemanager.FileChunk(file_path, sz, start, stop)
    return fchunk.read()
