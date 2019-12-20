META = {
    'command': 'dr',
    'command_description': 'Retrieve random release from user\'s collection.',
    'service': 'discogs',
    'service_endpoints': {
        'identity': 'https://api.discogs.com/oauth/identity',
        'collection': 'https://api.discogs.com/users/{username}/collection',
        'folders': 'https://api.discogs.com/users/{username}/collection/folders',
    },
    'slack_user_name': 'Discogs',
    'slack_icon_emoji': ':headphones:',
    'slack_payload_type': 'blocks',
    'slack_payload_structure': {
        'text': '*{artist} - {title}*\n<https://discogs.com{url}>\nMin: {price_min}; Med: {price_median}; Max: {price_max}',
        'image_url': '{image_url}',
        'alt_text': 'Release Thumb'
    },
    'command_steps': {
        1: {
            'name': 'get_user_name',
            'request_endpoint': 'identity',
            'request_parameters': {},
            'response_fields': {
                'username': 'username',
            },
        },
        2: {
            'name': 'get_item_count',
            'request_endpoint': 'folders',
            'request_parameters': {},
            'response_fields': {
                'count': 'folders.0.count',
            },
        },
        3: {
            'name': 'get_random_number',
            'function_call': 'random_from_range',
            'result_mapping': 'random'
        },
        4: {
            'name': 'get_random_release',
            'request_endpoint': 'collection',
            'request_parameters': {
                'page': '{random}',
                'per_page': 1,
            },
            'response_fields': {
                'id': 'releases.0.basic_information.id',
                'artist': 'releases.0.basic_information.artists_sort',
                'title': 'releases.0.basic_information.title',
                'url': 'releases.0.basic_information.url',
                'image_url': 'releases.0.basic_information.thumb',
                'price_min': 'releases.0.basic_information.sales_history.min.formatted',
                'price_max': 'releases.0.basic_information.sales_history.max.formatted',
                'price_median': 'releases.0.basic_information.sales_history.median.formatted',
            },
        }
    }
}


def random_from_range(count: int, **kwargs):
    from random import randrange
    return randrange(1, count)

