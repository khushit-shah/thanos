# sim/server.py

import simpy
from config import settings
from sim.utils import get_server_service_time

class Server:
    def __init__(self, env, network, ip_address):
        """
        Initialize a Server instance.

        Args:
            env (simpy.Environment): The simulation environment.
            network (Network): The network instance.
            ip_address (str): The server's IP address.
        """
        self.env = env
        self.network = network
        self.ip_address = ip_address
        self.type = 'server'
        self.network.register_entity(self.ip_address, self)
        
        # Initialize the request queue with capacity B
        self.queue = simpy.Store(env, capacity=settings.SERVER_BUFFER_SIZE)
        
        # Start the server process
        self.env.process(self.run())

        # TODO: Server's perfomance metrics should be added here.
    
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
                print(f"Server {self.ip_address} queue full. Dropping request from Client {message['client_id']} at time {self.env.now}")
                # Optionally, send an error message back to the sender
        else:
            print(f"Server {self.ip_address} received unknown message type at time {self.env.now}")
    
    def process_request(self, request):
        """Process a client request and send a response after a processing time."""
        # Simulate processing time
        service_time = get_server_service_time()
        yield self.env.timeout(service_time)
        
        src_entity = request['src_entity']
        message = request['message']
        
        # Create response message
        response_message = {
            'type': 'response',
            'data': 'response data',
            'server_ip': self.ip_address,
            'client_id': message['client_id'],
            'timestamp': self.env.now
        }
        
        # Determine where to send the response
        client_ip = message.get('client_ip')
        via_load_balancer = message.get('via_load_balancer', False)
        
        if via_load_balancer:
            # Send response back through the load balancer
            self.network.send(self.ip_address, settings.LOAD_BALANCER_IP, response_message)
        else:
            # Send response directly to the client
            self.network.send(self.ip_address, client_ip, response_message)
