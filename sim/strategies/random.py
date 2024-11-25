from .base_strategy import BaseStrategy
import random

class RandomStrategy(BaseStrategy):
    def __init__(self, server_ips):
        """
        Initialize the Round Robin strategy.

        Args:
            server_ips (list): List of server IP addresses.
        """
        self.server_ips = server_ips

    def get_next_server(self):
        """
        Get the next server IP address in round-robin order.

        Returns:
            str: The IP address of the selected server.
        """
        if not self.server_ips:
            raise ValueError("No servers registered with the RoundRobinStrategy.")
        
        random_idx = random.randint(0, len(self.server_ips) - 1)
        return self.server_ips[random_idx]

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
