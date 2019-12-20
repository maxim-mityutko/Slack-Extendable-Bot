from os import environ as env

META = {
    'service': 'mixcloud',
    'friendly_name': 'Mixcloud',
    'consumer_key': env.get('MIXCLOUD_CLIENT_ID'),
    'consumer_secret': env.get('MIXCLOUD_CLIENT_SECRET'),
    'endpoints': {
        'request_token': None,
        'authorize': 'https://www.mixcloud.com/oauth/authorize',
        'access_token': 'https://www.mixcloud.com/oauth/access_token',
    },
}

