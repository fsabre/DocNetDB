"""Define a logger for the package"""

import logging

logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    handlers=[logging.FileHandler("log.log"), logging.StreamHandler()],
)
