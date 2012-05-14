from joblauncher.lib import constants
from joblauncher.model import User, DBSession, Group
import ConfigParser
import tg, os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
import transaction


main_service = 'JOBLAUNCHER'

def init_services():
    configuration_file = constants.services_directory()
    print ' --- init services from %s ---' % configuration_file
    return ServiceManager(configuration_file)








class ServiceManager(object):

    def __init__(self, conf_file):
        self.services = [] # list of services
        self.parameters = {} # k, v of services parameters
        self.ips_allowed = [] # list of authorized IPS

        # read the configuration file
        config = ConfigParser.ConfigParser()
        config.read(conf_file)

        # configure default parameters
        self.in_path = config.get(main_service, 'in.path')
        self.out_path = config.get(main_service, 'out.path.default')

        # store parameters
        for service in config.sections():
            if not service == main_service:
                self.services.append(service)
                self.parameters[service] = {}
                for k, v in config.items(service):
                    self.parameters[service][k] = v.strip("'").strip('"')
                # mkdir tmp directories
                try :
                    os.mkdir(os.path.join(self.in_path, service))
                except OSError:
                    pass


        # store services on the database
        serv_group = DBSession.query(Group).filter(Group.id == constants.group_services_id).first()
        for service in self.services:
            contact = self.get(service, 'contact')
            serv = DBSession.query(User).filter(User.email == contact).first()
            if serv is None:
                serv = User()
                serv.name = service
                serv.email = contact
                serv.is_service = True
                DBSession.add(serv)
                serv_group.users.append(serv)
        DBSession.add(serv_group)
        DBSession.flush()
        transaction.commit()

    def get(self, service, param=None):
        """
        Get the service parameters. Or the param specified for the service specified.
        """
        if self.parameters.has_key(service):
            if param is not None:
                return self.parameters.get(service).get(param, None)
            return self.parameters.get(service)
        raise Exception("Service %s is not defined" % service)

    def check(self, param, value):
        """
        Check if the parameter specified with the value specified exist.
        If yes, it return the service.
        """
        for service in self.services:
            if self.get(service, param) == value: return service
        return False


service_manager = init_services()

from joblauncher.lib.services import io