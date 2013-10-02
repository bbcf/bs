import urllib2
import urllib
from bs.model import DBSession, Job
import tg
try:
    import simplejson as json
except ImportError:
    import json



DEBUG = True
def debug(s):
    if DEBUG:
        print s



# get url from configuration file
BIOREPO_SERVICE_URL = tg.config.get('biorepo.service.url')

BIOREPO_SERVICE_ACTION = 'public/extern_create'
BIOREPO_ACTION_URL = BIOREPO_SERVICE_URL + BIOREPO_SERVICE_ACTION
# if there is an url, biorepo service is ON
SERVICE_UP = False
if BIOREPO_SERVICE_URL:
    SERVICE_UP = True

def get_biorepo_url(task_id, result_id):
    return tg.url('/job/biorepo') + '?task_id=%s&result_id=%s' % (task_id, result_id)
    # result_id = int(result_id)
    # job = DBSession.query(Job).filter(Job.task_id == task_id).first()
    # for result in job.results:
    #     if result.id == result_id:
            
    # return ''


def request_to_biorepo(path, method='GET', data=None):
    if not SERVICE_UP:
        return
    url = BIOREPO_SERVICE_URL + path
    request = urllib2.Request(url)
    if data and method == 'POST':
        request.get_data = lambda: urllib.urlencode(json.loads(data))
    request.get_method = lambda: method
    return urllib2.urlopen(request)



def file_biorepo_request(fname, fparameters):
    data = {
        'fname': fname,
        'fparameters': fparameters}
    log = request_to_biorepo('/uploadfile', method='POST', data=data)
    return log

def file_biorepo_url(result):
    params = result.job.request.sanitized_parameter()
    fname = result.fname
    response = file_biorepo_request(fname, params)
    debug('[x] request to biorepo => %s <=' % (response.read()))
    return 'urltobiorepo'