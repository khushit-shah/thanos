# sim/network.py

import simpy
from config import settings
from sim.logger import setup_logger  # Import the logger

class Network:
    def __init__(self, env):
        self.env = env
        # Mapping of IP addresses to entity objects
        self.entities = {}
        # Mapping of entity objects to IP addresses
        self.ip_addresses = {}

        # Set up the logger
        self.logger = setup_logger('Network')

    def register_entity(self, ip_address, entity):
        """Register an entity with its IP address."""
        self.entities[ip_address] = entity
        self.ip_addresses[entity] = ip_address

    def get_entity_by_ip(self, ip_address):
        """Retrieve the entity object associated with an IP address."""
        return self.entities.get(ip_address)

    def get_ip_by_entity(self, entity):
        """Retrieve the IP address associated with an entity object."""
        return self.ip_addresses.get(entity)

    def send(self, src, dest, message):
        """Simulate sending a message from src to dest."""
        # Determine if src and dest are IP addresses or entities
        if isinstance(src, str):
            src_entity = self.get_entity_by_ip(src)
            src_ip = src
        else:
            src_entity = src
            src_ip = self.get_ip_by_entity(src_entity)

        if isinstance(dest, str):
            dest_entity = self.get_entity_by_ip(dest)
            dest_ip = dest
        else:
            dest_entity = dest
            dest_ip = self.get_ip_by_entity(dest_entity)

        if src_entity is None or dest_entity is None:
            raise ValueError("Source or destination not registered in the network.")

        # Determine transport delay based on src and dest
        delay = self.get_transport_delay(src_entity, dest_entity)

        # Schedule the delivery of the message
        self.env.process(self.deliver_message(src_entity, dest_entity, message, delay))

    def get_transport_delay(self, src_entity, dest_entity):
        """Calculate transport delay based on source and destination entities."""
        src_type = src_entity.type
        dest_type = dest_entity.type

        # Construct delay key
        if src_type == 'client' and dest_type == 'dns_server':
            delay_key = 'client_to_dns_server'
        elif src_type == 'dns_server' and dest_type == 'client':
            delay_key = 'dns_server_to_client'
        else:
            delay_key = f'{src_type}_to_{dest_type}'

        # Get the delay from settings
        delay = settings.TRANSPORT_DELAYS.get(delay_key, 0)
        return delay

    def deliver_message(self, src_entity, dest_entity, message, delay):
        """Deliver the message to the destination entity after the delay."""
        yield self.env.timeout(delay)
        # Log the message delivery
        if settings.LOGGING_ENABLED:
            src_ip = self.get_ip_by_entity(src_entity)
            dest_ip = self.get_ip_by_entity(dest_entity)
            self.logger.debug(
                f"Time {self.env.now}: Message delivered from {src_entity.type} "
                f"({src_ip}) to {dest_entity.type} ({dest_ip}). Message: {message}. Delay: {delay}"
            )
        # Pass the message to the destination entity
        dest_entity.receive_message(src_entity, message)
