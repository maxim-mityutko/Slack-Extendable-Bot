from common import logger, aws
from os import environ as env

logger = logger.init(__name__)


def configure():
    res = aws.resource('dynamodb')

    params = {'Table': 'config'}

    logger.info('Setting up environment variables for bot...')
    for config in aws.dynamodb_scan(resource=res, params=params):
        if config['type'].lower() == 'environment':
            env[config['parameter'].upper()] = config['value']
            logger.info('Environment variable \'{0}\' configured for bot.'.format(config['parameter'].upper()))

    params = {'Table': 'service'}

    logger.info('Setting up environment variables for services...')
    for service in aws.dynamodb_scan(resource=res, params=params):
        name = service['name']
        for key, value in service['oauth'].items():
            variable_name = '{0}_{1}'.format(name, key).upper()
            env[variable_name] = value
        logger.info('Environment variables configured for \'{0}\' service.'.format(name))
