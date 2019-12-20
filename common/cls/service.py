import oauth2 as oauth
from typing import Optional
import json
from dictor import dictor
import importlib
from urllib.parse import urlencode
import re

from common.cls.user import UserServiceConfig
from common import logger

logger = logger.init(__name__)


class Connector(object):
    def __init__(self, meta: dict, config: UserServiceConfig):
        self.service = meta['service']
        self.client_id = meta['consumer_key']
        self.client_secret = meta['consumer_secret']
        self.config = config
        self.client = Optional[oauth.Client]
        self.__module = meta['module']
        self.__client_call = meta['client_call'] if 'client_call' in meta and 'client_call' != '' else None
        self.__config = {}

    def init_client(self) -> bool:
        """
        Initialize client to connect to various services. By default standard OAuth2 client will be instantiated and
        client object will be saved in class instance. Custom clients are supported through a function call specified
        in meta.client_call node.
        :return: True if client init successful.
        """
        if self.__client_call is None:
            self.client = self.init_oauth_client()
        else:
            # Ideally these 4 attributes should be enough to instantiate any custom client, because they are just
            # wrappers around OAuth authenticators. If no, additional attributes can be exposed for future use.
            self.__config = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'token': self.config.oauth_token,
                'token_secret': self.config.oauth_token_secret
            }
            module = importlib.import_module(self.__module)
            self.client = getattr(module, self.__client_call)(**self.__config)
        logger.info('Instantiated {0} connector client for \'{1}\' service.'.format(type(self.client), self.service))
        return True

    def init_oauth_client(self) -> oauth.Client:
        """
        :return: OAuth2 client object.
        """
        consumer = oauth.Consumer(self.client_id, self.client_secret)
        token = oauth.Token(key=self.config.oauth_token, secret=self.config.oauth_token_secret)
        return oauth.Client(consumer, token)


class Payload(object):
    def __init__(self, meta: dict, connector: Connector):
        self.service = meta['service']
        self.service_endpoints = meta['service_endpoints'] if 'service_endpoints' in meta else None
        self.slack_user_name = meta['slack_user_name']
        self.slack_icon_emoji = meta['slack_icon_emoji']
        self.slack_payload_type = meta['slack_payload_type']  # Text / Blocks
        self.slack_payload_structure = meta['slack_payload_structure']
        self.command = meta['command']
        self.command_description = meta['command_description'] if 'command_description' in meta else None
        self.command_steps = meta['command_steps']
        self.connector = connector
        self.__module = meta['module']
        self.__content = {}
        self.__config = {}
        self.slack_payload = []

    def get_payload(self):
        logger.info('Command \'{command}\' triggered, connecting to \'{service}\' API...'
                    .format(command=self.command, service=self.service))
        if self.connector.init_client():
            self.__config.update(self.connector.config.misc)   # Load any user specific configuration stored DynamoDb.
            self.__config['connector'] = self.connector

            for seq, step in self.command_steps.items():
                if seq == len(self.command_steps):
                    step['payload'] = True   # Last step of the steps flow should always return the payload content.
                logger.info('>>>>> Executing step: \'{step}\''.format(step=step['name']))
                self.__step(client=self.connector.client, step=step)

            # print(self.__content)  # Debug spot

            self.__generate_message_payload()

    def __step(self, client: Optional[oauth.Client], step: dict):
        try:
            if 'request_endpoint' in step:
                self.__step__call_endpoint(client, step)
            elif 'function_call' in step:
                self.__step__call_function(step)
        except Exception as ex:
            logger.error(ex)

    def __step__call_endpoint(self, client: oauth.Client, step: dict):
        """
        Call API endpoint via OAuth client.
        :param client: Initialized OAuth client from Connector class.
        :param step: Step metadata loaded from payload file with an addition of certain workflow keys.
        :return:
        """
        # Generate URL by building the full string with {keys} that need to be replaced
        # and replace them with the contents of values dictionary.
        url = '{url}?{params}'\
            .format(
                url=self.service_endpoints[step['request_endpoint']],
                params=urlencode(step['request_parameters'], safe='{}')
            )\
            .format(**self.__config)

        response, content = client.request(url)
        if int(response['status']) == 200:
            for key, path in step['response_fields'].items():
                if 'payload' in step and step['payload']:
                    self.__content[key] = self.__get_value_from_json(content=content, path=path)
                else:
                    self.__config[key] = self.__get_value_from_json(content=content, path=path)
        else:
            logger.error('Status code \'{status}\' in step \'{name}\' for \'{endpoint}\': {message}'.format(
                name=step['name'], endpoint=step['request_endpoint'], status=response['status'],
                message=json.loads(content.decode('utf-8'))['message']))

    def __step__call_function(self, step: dict):
        """
        Call function specified in the step metadata.
        :param step: Step metadata.
        :return: Function execution result mapped to the key.
        """
        module = importlib.import_module(self.__module)
        result = getattr(module, step['function_call'], None)(**self.__config)
        if 'payload' in step and step['payload']:
            self.__content = result
        else:
            self.__config[step['result_mapping']] = result

    @staticmethod
    def __get_value_from_json(content: str, path: str):
        return dictor(json.loads(content.decode('utf-8')), path=path)

    def __generate_message_payload(self):
        if type(self.__content) == dict:
            self.__content = [self.__content]

        for item in self.__content:
            payload_item = {'username': self.slack_user_name, 'icon_emoji': self.slack_icon_emoji}
            if self.slack_payload_type == 'text':
                # By default all links within the message will be unfurled, but this should be avoided for
                # additional 'service_url' that link to the original post, hence the 'service_url_wo_protocol' key.
                # Refer to Slack API unfurling: https://api.slack.com/docs/message-link-unfurling#classic_unfurling
                if 'service_url' in item:
                    item['service_url_wo_protocol'] = re.sub(r'(^\w+:|^)\/\/', '', item['service_url'])
                payload_item['text'] = self.slack_payload_structure['text'].format(**item)
            elif self.slack_payload_type == 'blocks':
                blocks = [
                        {
                            'type': 'section',
                            'block_id': 'text',
                            'text': {
                                'type': 'mrkdwn',
                                'text': self.slack_payload_structure['text'].format(**item),
                            },
                            'accessory': {
                                'type': 'image',
                                'image_url': self.slack_payload_structure['image_url'].format(**item),
                                'alt_text': self.slack_payload_structure['alt_text'].format(**item)
                            }
                        }
                ]
                payload_item['blocks'] = blocks
            # print(payload_item)  # Debug spot
            self.slack_payload.append(payload_item)
