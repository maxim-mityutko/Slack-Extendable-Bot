from os import environ as env
from tweepy import OAuthHandler, API

# ==================================================================================================
# Required by 'core.auth' module
META = {
    'service': 'twitter',
    'friendly_name': 'Twitter',
    'consumer_key': env.get('TWITTER_CLIENT_ID'),
    'consumer_secret': env.get('TWITTER_CLIENT_SECRET'),
    'endpoints': {
        'request_token': 'https://api.twitter.com/oauth/request_token',
        'authorize': 'https://api.twitter.com/oauth/authorize',
        'access_token': 'https://api.twitter.com/oauth/access_token',
    },
    'client_call': 'init_client',
}
# ==================================================================================================
# Custom client if should be used, otherwise standard OAuth


def init_client(client_id: str, client_secret: str, token: str, token_secret: str, **kwargs) -> API:
    auth = OAuthHandler(client_id, client_secret)
    auth.set_access_token(token, token_secret)
    return API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# ==================================================================================================
