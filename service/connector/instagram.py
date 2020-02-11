from os import environ as env

META = {
    'service': 'instagram',
    'friendly_name': 'Instagram',
    'consumer_key': env.get('INSTAGRAM_CLIENT_ID'),
    'consumer_secret': env.get('INSTAGRAM_CLIENT_SECRET'),
    'endpoints': {
        'request_token': None,
        'authorize': 'https://api.instagram.com/oauth/authorize',
        'access_token': 'https://api.instagram.com/oauth/access_token',
    },
}

