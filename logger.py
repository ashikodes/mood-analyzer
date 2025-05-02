import os
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.mkdir("logs")

# Configure logging
log_file = "logs/moodsense.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3),
        logging.StreamHandler()
    ]
)

