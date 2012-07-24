# -*- coding: utf-8 -*-
"""Login controller."""

from bs.lib.base import BaseController
from bs.lib import tequila
from tg import expose,url,flash,request,response
from tg.controllers import redirect
from bs.model import User, Group, DBSession
from paste.auth import auth_tkt
from bs.config.app_cfg import token
from paste.request import resolve_relative_url
import transaction
import datetime
import tg
from bs.lib import constants

__all__ = ['LoginController']


class LoginController(BaseController):

    @expose('bs.templates.index')
    def index(self):
        '''
        Redirect user on tequila page in order to log him
        '''
        u = resolve_relative_url(url(), request.environ)
        res = tequila.create_request(u+'/login/auth','tequila.epfl.ch')
        redirect('https://tequila.epfl.ch/cgi-bin/tequila/requestauth?request'+res)

    @expose('bs.templates.index')
    def auth(self,came_from='/',**kw):
        '''
        Fetch user back from tequila.
        Validate the key from tequila.
        Log user.
        '''
        if not kw.has_key('key'):
            redirect(came_from)

        # take parameters
        key = kw.get('key')
        environ = request.environ
        authentication_plugins = environ['repoze.who.plugins']
        identifier = authentication_plugins['ticket']
        secret = identifier.secret
        cookiename = identifier.cookie_name
        remote_addr = environ['REMOTE_ADDR']
        # get user
        principal = tequila.validate_key(key,'tequila.epfl.ch')
        if not principal :
            redirect('/login/go')
        # build user from tequila response
        tmp_user = self.build_user(principal)
        mail = tmp_user.email
        # log or create him
        user = DBSession.query(User).filter(User.email == tmp_user.email).first()
        if user is None:
            user_group = DBSession.query(Group).filter(Group.id == constants.group_users_id).first()
            user_group.users.append(tmp_user)
            DBSession.add(tmp_user)
            DBSession.flush()
            user = DBSession.query(User).filter(User.email == mail).first()
            flash( '''Your account has been created''')
            DBSession.flush()

        elif user.name == constants.tmp_user_name:
            user.name = tmp_user.name
            user._set_date(datetime.datetime.now())
            user_group = DBSession.query(Group).filter(Group.id == constants.group_users_id).first()
            user_group.users.append(tmp_user)
            flash( '''Your account has been created''')
            DBSession.add(user)
            DBSession.flush()

        else :
            flash( 'Welcome back', 'notice')

        # user is logged now / look if he's an admin
        admins = tg.config.get('admin.mails')
        if admins is not None :
            group_admins = DBSession.query(Group).filter(Group.id == constants.group_admins_id).first()
            if user.email in admins:
                user not in group_admins.users and group_admins.users.append(user)
            else :
                user in group_admins.users and group_admins.users.remove(user)
            DBSession.flush()
        # create the authentication ticket
        user = DBSession.query(User).filter(User.email == mail).first()
        userdata=str(user.id)
        ticket = auth_tkt.AuthTicket(
                                       secret, user.email, remote_addr, tokens=token,
                                       user_data=userdata, time=None, cookie_name=cookiename,
                                       secure=True)
        val = ticket.cookie_value()
        # set it in the cookies
        response.set_cookie(
                     cookiename,
                     value=val,
                     max_age=None,
                     path='/',
                     domain=None,
                     secure=False,
                     httponly=False,
                     comment=None,
                     expires=None,
                     overwrite=False)

        redirect(came_from)

    @expose('bs.templates.index')
    def out(self):
        '''
        Logout the user.
        '''
        environ = request.environ
        authentication_plugins = environ['repoze.who.plugins']
        identifier = authentication_plugins['ticket']
        cookiename = identifier.cookie_name
        response.delete_cookie(cookiename)
        redirect('/')

    def build_user(self,principal):
        '''
        Build an User from a principal hash from Tequila
        @param principal: the hash from Tequila
        @return: an User
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('='))>1)
        user = User()
        if(hash.has_key('name')):
            user.name = hash.get('name')
        if(hash.has_key('email')):
            user.email = hash.get('email')
        if(hash.has_key('firstname')):
            user.firstname = hash.get('firstname')
        return user
