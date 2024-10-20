# sim/utils.py

import numpy as np
from config import settings

def get_client_request_interval():
    dist_name = settings.INITIAL_Q_DISTRIBUTION
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
    else:
        raise ValueError('Unsupported distribution')

def get_current_time(env):
    """Utility function to get the current simulation time."""
    return env.now

def get_load_balancer_processing_time():
    return max(0, np.random.normal(
        settings.LOAD_BALANCER_PROCESSING_TIME_MEAN,
        settings.LOAD_BALANCER_PROCESSING_TIME_STD
    ))

def get_server_service_time():
    return np.random.lognormal(
        mean=settings.SERVER_SERVICE_TIME_MEAN,
        sigma=settings.SERVER_SERVICE_TIME_STD
    )

def get_dns_service_time():
    # DNS service time may include load balancer processing time if DNS load balancer
    base_service_time = np.random.normal(settings.DNS_SERVICE_TIME_MEAN, settings.DNS_SERVICE_TIME_STD)
    if settings.LOAD_BALANCER_TYPE == 'dns':
        lb_service_time = np.random.normal(
            settings.LOAD_BALANCER_PROCESSING_TIME_MEAN,
            settings.LOAD_BALANCER_PROCESSING_TIME_STD
        )
        return max(0, base_service_time + lb_service_time)
    else:
        return max(0, base_service_time)