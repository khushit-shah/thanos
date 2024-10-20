# sim/logger.py

import logging
from config import settings

def setup_logger(name):
    """Set up and return a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.LOGGING_ENABLED else logging.CRITICAL)

    # Create handlers
    if settings.LOGGING_ENABLED:
        # File handler
        fh = logging.FileHandler(settings.LOG_FILE_PATH)
        fh.setLevel(logging.DEBUG)
        
        # Console handler (optional)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
