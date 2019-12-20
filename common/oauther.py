import oauth2 as oauth
import requests
import json
from urllib import parse
from urllib.parse import urlencode
import random

from common import logger

logger = logger.init('OAuthLogger')


class OAuthWrapper(object):
    def __init__(self,
                 consumer_key: str,
                 consumer_secret: str,
                 request_token_url: str,
                 authorize_url: str,
                 access_token_url: str,
                 user_agent: str,
                 connector_name: str,
                 callback_uri: str = None,
                 oauth_verifier: str = None,
                 ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_token_url = request_token_url
        self.authorize_url = authorize_url
        self.access_token_url = access_token_url
        self.user_agent = user_agent
        self.callback_uri = callback_uri
        self.connector_name = connector_name

        self.consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        self.oauth_token = None
        self.oauth_token_secret = None
        self.oauth_verifier = oauth_verifier

    def get_request_token(self):
        client = oauth.Client(self.consumer)
        response, content = client.request(self.request_token_url, 'POST', headers={'User-Agent': self.user_agent})

        if response['status'] != '200':
            logger.error('Invalid authentication response: {0}'.format(response['status']))

        request_token = dict(parse.parse_qsl(content))

        self.oauth_token = request_token[b'oauth_token'].decode('utf-8')
        self.oauth_token_secret = request_token[b'oauth_token_secret'].decode('utf-8')

        return True

    def get_authorization_url(self):
        if self.request_token_url is None:
            params = {
                'redirect_uri': self.callback_uri,
                'client_id': self.consumer_key,
                'response_type': 'code',
                'state': random.getrandbits(64),
            }
            log = 'Skipped 3-leg authorization'
        elif self.get_request_token():
            params = {
                'oauth_callback': self.callback_uri,
                'oauth_token': self.oauth_token,
            }
            log = 'Token requested successfully'
        url = '{url}?{params}'.format(url=self.authorize_url, params=urlencode(params))
        logger.info('{0}, authorization URL generated: {1}'.format(log, url))
        return url

    def get_access_token(self, **kwargs):
        if self.request_token_url is None:
            params = {
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.callback_uri,
                'code': self.oauth_verifier,
            }
            response = requests.post(self.access_token_url, params)

            if response.status_code != 200:
                logger.error('Invalid response while obtaining the access token: {0}'.format(response.text))
        else:
            token = oauth.Token(self.oauth_token, self.oauth_token_secret)
            token.set_verifier(self.oauth_verifier)
            client = oauth.Client(self.consumer, token)
            response, content = client.request(self.access_token_url, 'POST', headers={'User-Agent': self.user_agent})
            if int(response['status']) != 200:
                logger.error('Invalid response while obtaining the access token: {0}'.format(response['status']))

        if self.request_token_url is None:
            self.oauth_token = json.loads(response.text)['access_token']
        else:
            response_payload = dict(parse.parse_qsl(content))
            self.oauth_token = response_payload[b'oauth_token'].decode('utf-8')
            self.oauth_token_secret = response_payload[b'oauth_token_secret'].decode('utf-8')

        logger.info('Authentication complete!')
        return True

