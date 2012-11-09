from tg import request
from bs.model import DBSession, Connection
from bs.handler.user import get_user_in_session


def log_connection(fn):
    """
    Log the connection in the database.
    """


    def wrapped(self):
        user = get_user_in_session(request)
        conn = Connection()
        conn.user_id = user.id
        conn.ip = request.remote_addr
        conn.user_agent = request.user_agent
        conn.url = request.url
        conn.method = request.method
        conn.content_length = request.content_length
        conn.content_type = request.content_type
        conn.query_string = request.query_string
        conn.body = request.body
        DBSession.add(conn)
        return fn(self)
    return wrapped
