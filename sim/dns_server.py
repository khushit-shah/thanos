# sim/dns_server.py

import simpy
import random
from config import settings
from sim.utils import get_dns_service_time

class DNSServer:
    def __init__(self, env, network, ip_address, lb_strategy):
        """
        Initialize a DNSServer instance.

        Args:
            env (simpy.Environment): The simulation environment.
            network (Network): The network instance.
            ip_address (str): The DNS server's IP address.
            lb_strategy: The load-balancing strategy object.
        """
        self.env = env
        self.network = network
        self.ip_address = ip_address
        self.type = 'dns_server'
        self.network.register_entity(self.ip_address, self)
        
        # Initialize the request queue with capacity B
        self.queue = simpy.Store(env, capacity=settings.DNS_SERVER_BUFFER_SIZE)
        
        # Start the DNS server process
        self.env.process(self.run())
        
        # Load balancer type
        self.load_balancer_type = settings.LOAD_BALANCER_TYPE
        
        # Load balancing strategy
        self.lb_strategy = lb_strategy
        
    def run(self):
        """Process incoming DNS requests."""
        while True:
            # Wait for the next DNS request
            request = yield self.queue.get()
            # Process the request
            self.env.process(self.process_request(request))
    
    def receive_message(self, src_entity, message):
        """Handle incoming messages."""
        if message['type'] == 'dns_request':
            # Check if there's space in the queue
            if len(self.queue.items) < self.queue.capacity:
                # Enqueue the request
                self.queue.put({
                    'src_entity': src_entity,
                    'message': message,
                    'arrival_time': self.env.now
                })
            else:
                # TODO: the message should be dropped, the cliend must be notified about the drop.
                # Queue is full; drop the request
                print(f"DNS server queue full. Dropping request from Client {message['client_id']} at time {self.env.now}")
        else:
            print(f"DNS Server received unknown message type at time {self.env.now}")
    
    def process_request(self, request):
        """Process a DNS request and send a response after a service time."""
        # Simulate service time
        service_time = get_dns_service_time()
        yield self.env.timeout(service_time)
        
        src_entity = request['src_entity']
        message = request['message']
        
        # Determine the resolved IP based on load balancer type
        if self.load_balancer_type == 'dns':
            resolved_ip = self.lb_strategy.get_next_server()
        else:
            resolved_ip = settings.LOAD_BALANCER_IP  # Gateway load balancer IP
        
        # Create DNS response message
        response_message = {
            'type': 'dns_response',
            'ip': resolved_ip,
            'client_id': message['client_id'],
            'timestamp': self.env.now
        }
        
        # Send the response back to the client
        self.network.send(self.ip_address, self.network.get_ip_by_entity(src_entity), response_message)
