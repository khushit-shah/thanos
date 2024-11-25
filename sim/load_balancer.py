# sim/load_balancer.py

import simpy
from config import settings
from sim.utils import get_load_balancer_processing_time, get_load_balancer_response_processing_time
from sim.statistics import Statistics

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
        self.request_queue = simpy.Store(env, capacity=settings.LOAD_BALANCER_BUFFER_SIZE)
        
        # Initialize the response queue for responses coming back from servers
        self.response_queue = simpy.Store(env, capacity=settings.LOAD_BALANCER_BUFFER_SIZE)

        # Start the load balancer process for requests and responses
        self.env.process(self.run_request_processor())
        self.env.process(self.run_response_processor())
        
        # Load balancing strategy
        self.lb_strategy = lb_strategy
        self.cnt = 0

    def run_request_processor(self):
        """Process incoming client requests and forward them to a server."""
        while True:
            # Wait for the next request
            request = yield self.request_queue.get()

            Statistics.record_load_balancer_req_queue_size(self.env.now, len(self.request_queue.items))

            # Process the request
            yield self.env.process(self.process_request(request))

    def run_response_processor(self):
        """Process server responses and forward them to clients."""
        while True:
            # Wait for the next response from a server
            response = yield self.response_queue.get()

            Statistics.record_load_balancer_res_queue_size(self.env.now, len(self.response_queue.items))
            # Process the response
            yield self.env.process(self.process_response(response))
    
    def receive_message(self, src_entity, message):
        """Handle incoming messages."""
        if message['type'] == 'request':
            # Check if there's space in the request queue
            if len(self.request_queue.items) < self.request_queue.capacity:
                # Enqueue the request
                self.request_queue.put({
                    'src_entity': src_entity,
                    'message': message,
                    'arrival_time': self.env.now
                })
            else:
                # TODO: the message should be dropped, the cliend must be notified about the drop.
                # Queue is full; drop the request
                Statistics.increment_load_balancer_req_dropped_requests(self.env.now)
                self.network.send(self.ip_address, message['client_ip'], {"type": 'drop_server', 'data': 'queue full'})
                # Optionally, send an error message back to the client
            Statistics.record_load_balancer_req_queue_size(self.env.now, len(self.request_queue.items))
        elif message['type'] == 'response':
            # Check if there's space in the response queue
            if len(self.response_queue.items) < self.response_queue.capacity:
                # Enqueue the response
                self.response_queue.put({
                    'src_entity': src_entity,
                    'message': message,
                    'arrival_time': self.env.now
                })
            else:
                # Queue is full; drop the response
                Statistics.increment_load_balancer_res_dropped_requests(self.env.now)
                self.network.send(self.ip_address, message['client_ip'], {"type": 'drop_server', 'data': 'queue full'})
                # Optionally, log the dropped response
            Statistics.record_load_balancer_res_queue_size(self.env.now, len(self.response_queue.items))
        else:
            pass
    
    def process_request(self, request):
        self.cnt += 1
        print(self.cnt, end='\r')
        """Process a client request and forward it to a server after a processing time."""
        # Simulate processing time for the load balancer to forward the request
        processing_time = get_load_balancer_processing_time()
        yield self.env.timeout(processing_time)
        
        src_entity = request['src_entity']
        message = request['message']
        
        # Select a server IP using the load-balancing strategy
        server_ip = self.lb_strategy.get_next_server()
        
        # Modify the message to include the client IP so the server can send the response back
        message['client_ip'] = self.network.get_ip_by_entity(src_entity)
        message['through_lb'] = True
        
        # Send the request to the selected server
        self.network.send(self.ip_address, server_ip, message)

    def process_response(self, response):
        """Process a server response and forward it to the client after a processing time."""
        # Simulate processing time for the load balancer to forward the response
        processing_time = get_load_balancer_response_processing_time()
        yield self.env.timeout(processing_time)
        
        message = response['message']
        
        # Forward the response to the client
        client_ip = message['client_ip']
        self.network.send(self.ip_address, client_ip, message)
