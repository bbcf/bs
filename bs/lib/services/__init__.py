from bs.lib import constants
from bs import model
import ConfigParser
import os
import transaction


main_service = 'BIOSCRIPT'


class ServiceManager(object):

    def __init__(self, conf_file):
        self.services = []  # list of services
        self.parameters = {}  # k, v of services parameters
        self.ips_allowed = []  # list of authorized IPS

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
                try:
                    os.mkdir(os.path.join(self.in_path, service))
                except OSError:
                    pass

        # store services on the database
        for service in self.services:
            contact = self.get(service, 'contact')
            serv = model.DBSession.query(model.User).filter(model.User.email == contact).first()
            if serv is None:
                serv = model.User()
                serv.name = service
                serv.email = contact
                serv.is_service = True
                model.DBSession.add(serv)
        model.DBSession.flush()
        transaction.commit()

    def get(self, service, param=None, default=None):
        """
        Get the service parameters. Or the param specified for the service specified.
        """
        if service in self.parameters:
            return self.parameters.get(service).get(param, default)
        raise Exception("Service %s is not defined" % service)

    def check(self, param, value):
        """
        Check if the parameter specified with the value specified exist.
        If yes, it return the service.
        """
        for service in self.services:
            if self.get(service, param) == value:
                return service
        return False

configuration_file = constants.services_directory()
service_manager = ServiceManager(configuration_file)
