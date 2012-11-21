from tg import request
from bs.lib import constants, services, util
from bs import model
from sqlalchemy import and_


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
        conn.body = request.body
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
        if 'key' in request.str_POST or 'key' in request.str_GET:
            k = request.str_POST.get('key', request.str_GET.get('key'))
            service = services.service_manager.check(constants.SERVICE_SHARED_KEY, k)
            if service:
                user = model.DBSession.query(model.User).filter(
                    and_(model.User.name == service,
                        model.User.is_service == True)).first()
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
                # toto create user
            request.environ['bs-uid'] = user.id
            return fn(self, *args, **kw)
        raise Exception('Not identified')
    return wrapped
