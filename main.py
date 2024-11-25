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
from sim.strategies.least_connections import LeastConnectionsStrategy
from sim.strategies.random import RandomStrategy
from sim.statistics import Statistics

def add_clients(env, network, clients, num_clients):
    """Process to add clients one by one after random intervals."""
    for i in range(num_clients):
        # Random interval before adding the next client
        interval = random.expovariate(1.0 / settings.CLIENT_ARRIVAL_INTERVAL)
        yield env.timeout(interval)
        
        # Create the client and add it to the list
        client_ip = f'10.0.0.{i+1}'
        client = Client(env, network, client_ip, client_id=i+1)
        clients.append(client)
        # print(f"Client {i+1} added at time {env.now}")


import os

def main():
    os.system("rm output.csv")
    with open("output.csv", "a") as f:
        f.write("no_of_clients,strategy,type,service_time,cache_time,server_utilization,client_latency,server_queue_length,dropped_requests\n")

    for num_clients in [350, 400, 450, 500, 550, 600]:
        for strategy in ['round_robin', 'least_connections', 'random']:
            for type in ['gateway', 'dns']:
                for service_time in ['high', 'low']:
                        for cache_time in ['high', 'low']:
                            Statistics.clear_stats()
                            settings.NUMBER_OF_CLIENTS = num_clients
                            settings.LOAD_BALANCING_STRATEGY = strategy
                            settings.LOAD_BALANCER_TYPE = type

                            if service_time == 'high':
                                settings.SERVER_SERVICE_TIME_MEAN = 1.2
                            else:
                                settings.SERVER_SERVICE_TIME_MEAN = 0.6

                            if cache_time == 'high':
                                settings.CACHE_INVALIDATION_TIME = 500
                            else:
                                settings.CACHE_INVALIDATION_TIME = 200

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
                            elif settings.LOAD_BALANCING_STRATEGY == 'least_connections':
                                lb_strategy = LeastConnectionsStrategy(server_ips=[], network=network)
                            elif settings.LOAD_BALANCING_STRATEGY == 'random':
                                lb_strategy = RandomStrategy(server_ips=[])
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
                            env.process(add_clients(env, network, clients, settings.NUMBER_OF_CLIENTS))

                            
                            # ===============================
                            # Run the Simulation
                            # ===============================
                            # Start the simulation and run until SIMULATION_TIME
                            env.run(until=settings.SIMULATION_TIME)
                            
                            # ===============================
                            # Collect and Output Performance Metrics
                            # ===============================
                            # Statistics.generate_graphs()
                            # Statistics.print_summary_metrics(network)

                            with open("output.csv", "a") as f:
                                utilization = Statistics.get_avg_server_utilization(network)
                                latency = Statistics.get_avg_client_latencies()
                                queue_length = Statistics.get_average_server_queue_lengths(network)
                                dropped_requests = Statistics.get_dropped_requests()
                                f.write(f"{num_clients},{strategy},{type},{service_time},{cache_time},{utilization},{latency},{queue_length},{dropped_requests}\n")
                            print(f"{num_clients},{strategy},{type},{service_time},{cache_time},{utilization},{latency},{queue_length},{dropped_requests}\n")


if __name__ == '__main__':
    main()
