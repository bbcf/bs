'''
The authentication plugins for login in the application.
They are called in the 'who.ini' file
'''

import datetime
from codecs import utf_8_decode
from codecs import utf_8_encode
import os
import time

from paste.httpheaders import REQUEST_METHOD
from paste.request import get_cookies
from paste.auth import auth_tkt
from webob import Request, Response
from repoze.who.utils import resolveDotted
from zope.interface import implements
from joblauncher import handler
from joblauncher.lib import constants
from joblauncher.model import DBSession, User


from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator, IRequestClassifier
import zope.interface

app_token = 'JL'

from joblauncher.lib.services import service_manager



def make_plugin_auth(check_fn=None):
    '''
    Build the authentifier plugin
    '''
    return SharedKeyPlugin()




class SharedKeyPlugin(object):
    '''
    A custom plugin for authentication from command line.
    '''
    implements(IIdentifier, IChallenger, IAuthenticator)
    # IIdentifier
    def identify(self, environ):
        '''
        Identify the user
        '''
        request = Request(environ)
        if 'key' in request.str_POST:
            k =  request.str_POST.get('key')
            service = service_manager.check(constants.SERVICE_SHARED_KEY, k)
            if not service:
                return None
            user = DBSession.query(User).filter(User.name == service).first()
            if user is None:
                return None

            identity = {}
            identity['repoze.who.userid'] = user.email
            identity['tokens'] = app_token
            identity['userdata'] = user.id
            environ['auth'] = True
            return identity

        return None

    # IIdentifier
    def forget(self, environ, identity):
        '''
        Forget the user
        '''
        pass
        # IIdentifier
    def remember(self, environ, identity):
        '''
        Remember the user. (no remember from command line)
        '''

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        '''
        The challenger.
        '''
        res = Response()
        res.headerlist = [('Content-type', 'application/json')]
        res.charset = 'utf8'
        res.unicode_body = u"{error:'wrong credentials'}"
        res.status = 403
        return res

    def authenticate(self, environ, identity):
        '''
        Authenticate
        '''
        pass

def request_classifier(environ):
    '''
    Returns one of the classifiers 'command_line' or 'browser',
    depending on the imperative logic below
    '''
    return constants.REQUEST_TYPE_SERVICE

zope.interface.directlyProvides(request_classifier, IRequestClassifier)