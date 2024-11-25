# sim/utils.py

import numpy as np
from config import settings
import random
def get_client_request_interval():

    dist_name = random.choice(list(settings.Q_DISTRIBUTIONS.keys()))

    params = settings.Q_DISTRIBUTIONS[dist_name]
    
    if dist_name == 'normal':
        return max(0, np.random.normal(params['mean'], params['std']))
    elif dist_name == 'exponential':
        return np.random.exponential(params['scale'])
    elif dist_name == 'uniform':
        return np.random.uniform(params['low'], params['high'])
    elif dist_name == 'gamma':
        return np.random.gamma(params['shape'], params['scale'])
    elif dist_name == 'chi_squared':
        return np.random.chisquare(params['df'])
    elif dist_name == 'burst':
        return params
    else:
        raise ValueError('Unsupported distribution')

def get_current_time(env):
    """Utility function to get the current simulation time."""
    return env.now

def get_lb_strategy_processing_time():
    return np.random.exponential(settings.LOAD_BALANCING_STRATEGY_PROCESSING_TIME[settings.LOAD_BALANCING_STRATEGY]['mean'])

def get_load_balancer_processing_time():
    return get_lb_strategy_processing_time() + max(0, np.random.exponential(settings.LOAD_BALANCER_PROCESSING_TIME_MEAN))

def get_load_balancer_response_processing_time():
    return max(0, np.random.exponential(settings.LOAD_BALANCER_PROCESSING_TIME_MEAN))

def get_server_service_time():
    return np.random.exponential(settings.SERVER_SERVICE_TIME_MEAN)

def get_dns_service_time():
    # DNS service time may include load balancer processing time if DNS load balancer
    base_service_time = max(0, np.random.exponential(settings.DNS_SERVICE_TIME_MEAN))
    if settings.LOAD_BALANCER_TYPE == 'dns':
        lb_service_time = get_lb_strategy_processing_time()
        return max(0, base_service_time + lb_service_time)
    else:
        return max(0, base_service_time)