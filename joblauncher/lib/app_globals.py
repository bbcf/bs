# -*- coding: utf-8 -*-
from joblauncher.lib.plugins import init_plugins


"""The application's Globals object"""

#from joblauncher.websetup.bootstrap import group_admins, group_users, perm_admin, perm_user

__all__ = ['Globals']





class Globals(object):

    """Container for objects available throughout the life of the application.



    One instance of Globals is created during application initialization and

    is available during requests via the 'app_globals' variable.



    """



    def __init__(self):

      self.plugin_manager = init_plugins()
