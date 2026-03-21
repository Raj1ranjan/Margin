import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(logs_dir, f"margin_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console for development
    ]
)

logger = logging.getLogger("Margin")

def log_operation(operation, details=""):
    """Log a successful operation"""
    logger.info(f"Operation completed: {operation} - {details}")

def log_error(operation, error, details=""):
    """Log an error"""
    logger.error(f"Operation failed: {operation} - {error} - {details}")

def log_info(message):
    """Log general information"""
    logger.info(message)