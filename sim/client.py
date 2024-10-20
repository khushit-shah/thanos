# sim/client.py

import simpy
import random
import numpy as np
from config import settings
from sim.utils import get_client_request_interval

class Client:
    def __init__(self, env, network, ip_address, client_id):
        """
        Initialize a Client instance.

        Args:
            env (simpy.Environment): The simulation environment.
            network (Network): The network instance.
            ip_address (str): The client's IP address.
            client_id (int): A unique identifier for the client.
        """
        self.env = env
        self.network = network
        self.ip_address = ip_address
        self.client_id = client_id
        self.type = 'client'
        self.network.register_entity(self.ip_address, self)
        
        # DNS cache variables
        self.cached_ip = None
        self.cache_timestamp = None
        self.cache_valid = False
        
        # Events for synchronization
        self.dns_response_event = self.env.event()
        self.response_event = self.env.event()
        
        # Metrics
        self.metrics = {
            'request_times': [],
            'response_times': [],
            'latencies': [],
            'session_start_time': self.env.now,
        }
        
        # Start the client process
        self.env.process(self.run())
    
    def run(self):
        """Simulate the client's behavior."""
        while True:
            # Decide whether to terminate
            if random.random() < settings.CLIENT_TERMINATION_PROBABILITY:
                # Log termination
                print(f"Client {self.client_id} terminating at time {self.env.now}")
                break  # Client terminates
            
            # Time when the request starts
            request_start_time = self.env.now
            
            # Check DNS cache validity
            if self.cache_valid and (self.env.now - self.cache_timestamp) < settings.CACHE_INVALIDATION_TIME:
                # Use cached IP
                resolved_ip = self.cached_ip
            else:
                # Send DNS request
                self.dns_response_event = self.env.event()  # Reset the event
                dns_request_message = {
                    'type': 'dns_request',
                    'domain': 'example.com',
                    'client_id': self.client_id,
                    'timestamp': self.env.now
                }
                self.network.send(self.ip_address, settings.DNS_SERVER_IP, dns_request_message)
                # Wait for DNS response
                yield self.dns_response_event
                resolved_ip = self.cached_ip  # Updated in receive_message
                
            # Send request to resolved IP
            self.response_event = self.env.event()  # Reset the event
            request_message = {
                'type': 'request',
                'data': '...',
                'client_id': self.client_id,
                'timestamp': self.env.now
            }
            self.network.send(self.ip_address, resolved_ip, request_message)
            # Wait for response
            yield self.response_event
            
            # Calculate latency and log metrics
            response_time = self.env.now
            latency = response_time - request_start_time
            self.metrics['request_times'].append(request_start_time)
            self.metrics['response_times'].append(response_time)
            self.metrics['latencies'].append(latency)
            
            print(f"Client {self.client_id} received response at time {self.env.now:.4f}, latency: {latency:.4f} seconds")
            
            # Wait for time q before next request
            q = get_client_request_interval()
            yield self.env.timeout(q)
    
    def receive_message(self, src_entity, message):
        """Handle incoming messages."""
        if message['type'] == 'dns_response':
            # Update cache
            self.cached_ip = message['ip']
            self.cache_timestamp = self.env.now
            self.cache_valid = True
            # Signal that DNS response has been received
            self.dns_response_event.succeed()
        elif message['type'] == 'response':
            # Signal that the response has been received
            self.response_event.succeed()
        else:
            print(f"Client {self.client_id} received unknown message type at time {self.env.now}")
