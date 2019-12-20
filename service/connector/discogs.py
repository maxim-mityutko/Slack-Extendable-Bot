from os import environ as env

META = {
    'service': 'discogs',
    'friendly_name': 'Discogs',
    'consumer_key': env.get('DISCOGS_CLIENT_ID'),
    'consumer_secret': env.get('DISCOGS_CLIENT_SECRET'),
    'endpoints': {
        'request_token': 'https://api.discogs.com/oauth/request_token',
        'authorize': 'https://www.discogs.com/oauth/authorize',
        'access_token': 'https://api.discogs.com/oauth/access_token',
    },
}
