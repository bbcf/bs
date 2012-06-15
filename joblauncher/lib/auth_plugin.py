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
        # SERVICE DEFINED
        if 'key' in request.str_POST or 'key' in request.str_GET:
            k =  request.str_POST.get('key', request.str_GET.get('key'))
            service = service_manager.check(constants.SERVICE_SHARED_KEY, k)
            if service is not None:
                user = DBSession.query(User).filter(User.name == service).first()
                if user is not None:
                    identity = {}
                    identity['repoze.who.userid'] = user.email
                    identity['tokens'] = app_token
                    identity['userdata'] = user.id
                    environ['auth'] = True
                    return identity

        # SINGLE USER
        if 'REMOTE_ADDR' in environ:
            remote = environ['REMOTE_ADDR']
            identity = {}
            identity['repoze.who.userid'] = remote
            identity['tokens'] = app_token
            identity['userdata'] = remote
            environ['auth'] = True
            user = DBSession.query(User).filter(User.name == remote).first()
            if user is None:
                handler.user.create_user(remote, remote)
            return identity


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
        pass

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