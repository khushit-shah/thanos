# sim/load_balancer.py

import simpy
from config import settings
from sim.utils import get_load_balancer_processing_time

class LoadBalancer:
    def __init__(self, env, network, ip_address, lb_strategy):
        """
        Initialize a LoadBalancer instance.

        Args:
            env (simpy.Environment): The simulation environment.
            network (Network): The network instance.
            ip_address (str): The load balancer's IP address.
            lb_strategy: The load-balancing strategy object.
        """
        self.env = env
        self.network = network
        self.ip_address = ip_address
        self.type = 'load_balancer'
        self.network.register_entity(self.ip_address, self)
        
        # Initialize the request queue with capacity B
        self.queue = simpy.Store(env, capacity=settings.LOAD_BALANCER_BUFFER_SIZE)
        
        # Start the load balancer process
        self.env.process(self.run())
        
        # Load balancing strategy
        self.lb_strategy = lb_strategy

    def run(self):
        """Process incoming requests."""
        while True:
            # Wait for the next request
            request = yield self.queue.get()
            # Process the request
            self.env.process(self.process_request(request))
    
    def receive_message(self, src_entity, message):
        """Handle incoming messages."""
        if message['type'] == 'request':
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
                print(f"Load balancer queue full. Dropping request from Client {message['client_id']} at time {self.env.now}")
                # Optionally, send an error message back to the client
        elif message['type'] == 'response':
            # Forward the response back to the client
            client_ip = message['client_ip']
            self.network.send(self.ip_address, client_ip, message)
        else:
            print(f"Load Balancer received unknown message type at time {self.env.now}")

    def process_request(self, request):
        """Process a client request and forward it to a server after a processing time."""
        # Simulate processing time
        processing_time = get_load_balancer_processing_time()
        yield self.env.timeout(processing_time)
        
        src_entity = request['src_entity']
        message = request['message']
        
        # Select a server IP using the strategy
        server_ip = self.lb_strategy.get_next_server()
        
        # Modify the message to include client IP so the server can send the response back
        message['client_ip'] = self.network.get_ip_by_entity(src_entity)
        
        # Send the request to the selected server
        self.network.send(self.ip_address, server_ip, message)
