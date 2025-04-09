""" This module provides a class to manage a list of services """
import uuid
from datetime import datetime


class Services:
    """
    manages a list of registered services
    """
    def __init__(self):
        """
        constructor for the Services class
        """
        self._service_list = []

    def register(self, type, ipaddr, port):
        """
        registers a service
        :param type: A keyword to define the type of service
        :param ipaddr: IPv4 or IPv6 address of the service
        :param port: Portnumber where the service can be reached
        :return: UUID identifying the service, must be supplied for 'heartbeat'
        """
        service_uuid = str(uuid.uuid4())
        self._service_list.append({
            'uuid': service_uuid,
            'type': type,
            'ip': ipaddr,
            'port': port,
            'heartbeat': datetime.now()
        })
        return service_uuid

    def heartbeat(self, service_uuid):
        """
        updates the heartbeat for a service
        :param service_uuid: UUID identifying the service
        :return: 'OK' / 'NOT FOUND'
        """
        for service in self._service_list:
            if service['uuid'] == service_uuid:
                service['heartbeat'] = datetime.now()
                return 'OK'
        return 'NOT FOUND'

    def query(self, type):
        """
        Query the list for all active services of a certain type
        :param type: A keyword to identify the services
        :return: A list of dictionaries with the ip-address and the port of each service
        """
        results = []
        for service in self._service_list:
            duration = datetime.now() - service['heartbeat']
            if duration.total_seconds() > 5:
                self._service_list.remove(service)
        return str(results)
