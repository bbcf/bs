# -*- coding: utf-8 -*-
"""user handler"""
from joblauncher.model.auth import User, Group
from joblauncher.model import DBSession
from tg import abort
from sqlalchemy import and_
from joblauncher.lib import constants
import transaction


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
    user = DBSession.query(User).filter(User.email == email).first()
    return user




def create_user(name, email):
    serv = User()
    serv_group = DBSession.query(Group).filter(Group.id == constants.group_services_id).first()
    serv.name = name
    serv.email = email
    serv.is_service = False
    DBSession.add(serv)
    serv_group.users.append(serv)
    DBSession.add(serv_group)
    DBSession.flush()
    transaction.commit()
    # create directory
    from joblauncher.lib.services import service_manager
    import os
    try :
        os.mkdir(os.path.join(service_manager.in_path, name))
    except OSError:
        pass