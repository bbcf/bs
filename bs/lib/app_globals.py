# -*- coding: utf-8 -*-

"""The application's Globals object"""

#from bs.websetup.bootstrap import group_admins, group_users, perm_admin, perm_user

__all__ = ['Globals']





class Globals(object):

    """Container for objects available throughout the life of the application.



    One instance of Globals is created during application initialization and

    is available during requests via the 'app_globals' variable.



    """



    def __init__(self):
        pass
