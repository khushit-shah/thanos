from .base_strategy import BaseStrategy
import random

class LeastConnectionsStrategy(BaseStrategy):
    def __init__(self, server_ips, network):
        """
        Initialize the Round Robin strategy.

        Args:
            server_ips (list): List of server IP addresses.
        """
        self.server_ips = server_ips
        self.network = network

    def get_next_server(self):
        """
        Get the next server IP address in round-robin order.

        Returns:
            str: The IP address of the selected server.
        """
        if not self.server_ips:
            raise ValueError("No servers registered with the RoundRobinStrategy.")
        
        # Find the server with the least number of connections
        min_connections = float('inf')
        selected_server = None
        for server_ip in self.server_ips:
            connections = self.network.get_entity_by_ip(server_ip).get_connections()
            if connections < min_connections:
                min_connections = connections
                selected_server = server_ip
        return selected_server

    def register_server(self, server_ip):
        """
        Register a new server IP address with the strategy.

        Args:
            server_ip (str): The IP address of the server to add.
        """
        self.server_ips.append(server_ip)

    def remove_server(self, server_ip):
        """
        Remove a server IP address from the strategy.

        Args:
            server_ip (str): The IP address of the server to remove.
        """
        self.server_ips.remove(server_ip)
        # Adjust current_index if necessary
        self.current_index = self.current_index % len(self.server_ips)
