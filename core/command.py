import re

from common.cls.service import Connector, Payload
from core import auth
from common import logger

logger = logger.init(__name__)


def get_payload(connectors: dict, payloads: dict, command: str, user: str):
    command = if_command_exists(payloads=payloads, command=command)
    if command is None:
        return exception_payload(type='UNKNOWN')
    elif command == 'help':
        text = ''
        for key, value in payloads.items():
            print(value)
            text += '{command}:\t{description}\n'\
                .format(command=key, description=value['meta']['command_description'])
        return [{'text': text}]

    payload_meta = payloads[command]['meta']

    config = auth.get_config(payload_meta['service'], user)
    if config is None:
        return exception_payload(type='NOT_AUTHORIZED', payload_meta=payload_meta)

    connector_meta = connectors[payload_meta['service']]['meta']
    connector = Connector(connector_meta, config)

    pld = Payload(payload_meta, connector)
    pld.get_payload()
    if len(pld.slack_payload) == 0:
        return exception_payload(type='EMPTY_RESPONSE', payload_meta=payload_meta)

    return pld.slack_payload


def exception_payload(type: str, **kwargs):
    if 'payload_meta' in kwargs:
        user_name = kwargs['payload_meta']['slack_user_name']
        icon_emoji = kwargs['payload_meta']['slack_icon_emoji']

    if type == 'UNKNOWN':
        logger.info('Trigger: COMMAND_CORE__UNKNOWN')
        return [{
            'text': 'Command unknown, use /help to get the list of available actions.'
        }]

    if type == 'NOT_AUTHORIZED':
        logger.info('Trigger: COMMAND_CORE__NOT_AUTHORIZED')
        return [{
            'username': user_name, 'icon_emoji': icon_emoji, 'text': 'Bot is not authorized to use this service...'
        }]

    if type == 'EMPTY_RESPONSE':
        return [
            {
                'username': user_name, 'icon_emoji': icon_emoji,
                'text': 'Service returned no results, try later...'
            }
        ]
    '''
    if type == 'ERROR':
        return [
            {
                'text': 'Something went wrong: {0}'.format(str(ex)),
                'icon_emoji': ':exclamation:'
            }
        ]

        if '401' in str(ex) or '403' in str(ex):
            payload = [
                {
                    'username': command['username'],
                    'text': 'Bot is not authorized to use this service, authenticate and try again',
                    'icon_emoji': ':exclamation:'
                }
            ]
            logger.error(ex)
    '''


def if_command_exists(payloads: dict, command: str):
    command = re.search(r'\/.*$', command)[0].replace('/', '').split()[0]
    if command in payloads or command == 'help':
        return command
    else:
        return None
