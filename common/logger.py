import logging
from os import environ as env


# Instantiate logger
def init(name: str):
    # Setup logging
    if 'LOGGING_LEVEL' in env:
        level = logging.getLevelName(env['LOGGING_LEVEL'])
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level, format='%(levelname)-7s %(name)-22s %(message)s', style='%'
    )
    return logging.getLogger(name)
