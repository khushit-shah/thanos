# config/settings.py

import numpy as np

# ===============================
# General Simulation Settings
# ===============================

# Random Seed for reproducibility
RANDOM_SEED = 42

# Total simulation time (in seconds)
SIMULATION_TIME = 10000


# Number of Servers in the simulation
NUMBER_OF_SERVERS = 5
SERVER_IPS = [f'192.168.1.{i+3}' for i in range(NUMBER_OF_SERVERS)]

# Load Balancer Type: 'gateway' or 'dns'
LOAD_BALANCER_TYPE = 'gateway'  # Options: 'gateway', 'dns'

# Load Balancing Strategy
LOAD_BALANCING_STRATEGY = 'round_robin'  # Options: 'round_robin', 'least_connections', etc.

# Load Balancer IP Address
LOAD_BALANCER_IP = '192.168.0.2'

# ===============================
# Client Settings
# ===============================

# Number of Clients in the simulation
NUMBER_OF_CLIENTS = 1000

# Client Termination Probability
CLIENT_TERMINATION_PROBABILITY = 0.01  # Probability that a client terminates after a request

# Cache Settings
CACHE_INVALIDATION_TIME = 300  # Time in seconds before DNS cache is invalidated

# Client Inter-request Time (q)
# Define distributions and their parameters for generating q
Q_DISTRIBUTIONS = {
    'normal': {'mean': 5, 'std': 1},
    'exponential': {'scale': 5},
    'uniform': {'low': 1, 'high': 10},
    'gamma': {'shape': 2, 'scale': 2},
    'chi_squared': {'df': 2}
}

# Initial distribution to use for q
INITIAL_Q_DISTRIBUTION = 'exponential'  # Choose from Q_DISTRIBUTIONS keys

# Client Inter-arrival Time Distribution Parameters
CLIENT_INTERARRIVAL_TIME_MEAN = 1  # Mean inter-arrival time in seconds
CLIENT_INTERARRIVAL_TIME_STD = 0.5  # Standard deviation

# ===============================
# DNS Server Settings
# ===============================

# DNS Service Time Distribution (including load balancer processing time if DNS load balancer)
DNS_SERVICE_TIME_MEAN = 0.01  # Mean service time in seconds
DNS_SERVICE_TIME_STD = 0.005   # Standard deviation

# DNS Server Queue Capacity (B in G/G/1/B queue)
DNS_SERVER_BUFFER_SIZE = 1000  # Maximum number of DNS requests in the queue

# DNS Server IP Address
DNS_SERVER_IP = '192.168.0.1'


# ===============================
# Server Settings
# ===============================

# Server Processing Time Distribution (Log-Normal)
# Note: For a log-normal distribution, the mean and std are for the underlying normal distribution
SERVER_SERVICE_TIME_MEAN = 2.0  # Mean of the underlying normal distribution
SERVER_SERVICE_TIME_STD = 0.1   # Standard deviation of the underlying normal distribution

# Server Queue Capacity (B in x/G/1/B queue)
SERVER_BUFFER_SIZE = 100  # Maximum number of requests in the server queue

# ===============================
# Load Balancer Settings
# ===============================

# Load Balancer Processing Time Distribution (Gaussian)
LOAD_BALANCER_PROCESSING_TIME_MEAN = 0.01  # Mean processing time in seconds
LOAD_BALANCER_PROCESSING_TIME_STD = 0.005  # Standard deviation

# Load Balancer Queue Capacity (if applicable)
LOAD_BALANCER_BUFFER_SIZE = 1000000000  # Maximum number of requests in the load balancer queue

# ===============================
# Network Transport Delays
# ===============================

# Delays in seconds between different entities
TRANSPORT_DELAYS = {
    'client_to_load_balancer': 0.1,
    'load_balancer_to_server': 0.05, # should be internal.
    'server_to_load_balancer': 0.05,
    'load_balancer_to_client': 0.1,
    'client_to_dns': 0.05,  # Used if DNS request is sent
}

# ===============================
# Miscellaneous Settings
# ===============================

# Logging Settings
LOGGING_ENABLED = True  # Enable or disable logging
LOG_FILE_PATH = 'data/logs/simulation.log'

# Output Settings
OUTPUT_METRICS_FILE = 'data/outputs/performance_metrics.csv'