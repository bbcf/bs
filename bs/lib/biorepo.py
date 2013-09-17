import urllib2
import urllib
try:
    import simplejson as json
except ImportError:
    import json

import tg



DEBUG = True
def debug(s):
    if DEBUG:
        print s


# get url from configuration file
BIOREPO_SERVICE_URL = tg.config('biorepo.service.url')
# if there is an url, biorepo service is ON
SERVICE_UP = False
if BIOREPO_SERVICE_URL:
    SERVICE_UP = True


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