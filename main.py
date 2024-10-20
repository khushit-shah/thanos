# main.py

import simpy

import random
import numpy as np

from config import settings

from sim.network import Network
from sim.client import Client
from sim.server import Server
from sim.dns_server import DNSServer
from sim.load_balancer import LoadBalancer

from sim.strategies.round_robin import RoundRobinStrategy

def main():
    # ===============================
    # Initialize the Simulation Environment
    # ===============================
    env = simpy.Environment()
    
    # Set random seeds for reproducibility
    random.seed(settings.RANDOM_SEED)
    np.random.seed(settings.RANDOM_SEED)
    
    # ===============================
    # Create the Network
    # ===============================
    network = Network(env)
    
    # ===============================
    # Configure the Load-Balancing Strategy
    # ===============================
    # Initialize the load-balancing strategy based on settings
    if settings.LOAD_BALANCING_STRATEGY == 'round_robin':
        lb_strategy = RoundRobinStrategy(server_ips=[])
    else:
        raise ValueError(f"Unsupported load balancing strategy: {settings.LOAD_BALANCING_STRATEGY}")
    
    # ===============================
    # Create and Register DNS Server
    # ===============================
    dns_server = DNSServer(env, network, settings.DNS_SERVER_IP, lb_strategy)
    
    # ===============================
    # Create and Register Load Balancer (if using gateway load balancer)
    # ===============================
    if settings.LOAD_BALANCER_TYPE == 'gateway':
        load_balancer = LoadBalancer(env, network, settings.LOAD_BALANCER_IP, lb_strategy)
    else:
        load_balancer = None  # Not needed for DNS load balancing
    
    # ===============================
    # Create and Register Servers
    # ===============================
    servers = []
    for ip in settings.SERVER_IPS:
        server = Server(env, network, ip)
        servers.append(server)
        lb_strategy.register_server(ip)
    
    # ===============================
    # Create and Register Clients
    # ===============================
    clients = []
    for i in range(settings.NUMBER_OF_CLIENTS):
        client_ip = f'10.0.0.{i+1}'
        client = Client(env, network, client_ip, client_id=i+1)
        clients.append(client)
    
    # ===============================
    # Run the Simulation
    # ===============================
    # Start the simulation and run until SIMULATION_TIME
    env.run(until=settings.SIMULATION_TIME)
    
    # ===============================
    # Collect and Output Performance Metrics
    # ===============================
    # TODO: Implement metric collection and output

if __name__ == '__main__':
    main()
