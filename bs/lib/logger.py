from tg import request
from bs.lib import constants, services, util
from bs import model
from sqlalchemy import and_

import time


def timeit(n):
    def wrapped(fn):
        def wrapper(*args, **kw):
            ts = time.time()
            result = fn(*args, **kw)
            te = time.time()
            if n > 0:
                print '[x] TIME [x] %r %2.2f sec [x]' % (fn.__name__, te-ts)
            return result
        return wrapper
    return wrapped


def log_connection(fn):
    """
    Log the connection in the database.
    """

    def wrapped(self, *args, **kw):
        user = util.get_user(request)
        conn = model.Connection()
        conn.user_id = user.id
        conn.ip = request.remote_addr
        conn.user_agent = request.user_agent
        conn.url = request.url
        conn.method = request.method
        conn.content_length = request.content_length
        conn.content_type = request.content_type
        conn.query_string = request.query_string
        conn.body = ','.join(['%s:%s' % (k, v) for k, v in request.params.iteritems()])
        model.DBSession.add(conn)
        return fn(self, *args, **kw)
    return wrapped


def identify(fn):
    """
    Identify the user.
    """
    def wrapped(self, *args, **kw):
        if 'bs-uid' in request.environ:
            return fn(*args, **kw)
        # SERVICE DEFINED
        k = None
        if 'key' in request.POST or 'key' in request.GET:
            k = request.POST.get('key', request.GET.get('key'))
            service = services.service_manager.check(constants.SERVICE_SHARED_KEY, k)
            if service:
                user = model.DBSession.query(model.User).filter(
                    and_(model.User.name == service,
                        model.User.is_service == True)).first()
                if not user:
                    print '[x] service not found in the database.'
                request.environ['bs-uid'] = user.id
                return fn(self, *args, **kw)

        if k:
            user = model.DBSession.query(model.User).filter(model.User.key == k).first()
            if not user:
                print '[x] Key %s given but not found in the database. Perhaps the service needs to be declared in service.ini file.' % k
            request.environ['bs-uid'] = user.id
            return fn(self, *args, **kw)

        if 'REMOTE_ADDR' in request.environ:
            remote = request.environ['REMOTE_ADDR']
            user = model.DBSession.query(model.User).filter(model.User.remote == remote).first()
            if user is None:
                user = model.User()
                user.name = 'anonymous'
                user.is_service = False
                user.remote = remote
                model.DBSession.add(user)
                model.DBSession.flush()
            request.environ['bs-uid'] = user.id
            return fn(self, *args, **kw)

        raise Exception('Not identified')
    return wrapped
