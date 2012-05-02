# -*- coding: utf-8 -*-
"""user handler"""
from joblauncher.model.auth import User
from joblauncher.model import DBSession
from tg import abort
from sqlalchemy import and_
from joblauncher.lib import constants


def get_user_in_session(request):
    '''
    Get the user that is performing the current request
    @param request: the web request
    @type request: a WebOb
    '''

    if not 'repoze.who.identity' in request.environ :
        abort(401)
    identity = request.environ['repoze.who.identity']
    email = identity['repoze.who.userid']
    user = DBSession.query(User).filter(User.email == email).first()
    return user


def get_service_in_session(request):
    '''
    Get the user that is performing the current request
    @param request: the web request
    @type request: a WebOb
    '''

    if not 'repoze.who.identity' in request.environ :
        abort(401)
    identity = request.environ['repoze.who.identity']
    email = identity['repoze.who.userid']
    user = DBSession.query(User).filter(User.email == constants.service_email(email)).first()
    return user




