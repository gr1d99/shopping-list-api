from app import APP
from waitress import serve

import logging
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)


serve(APP)
