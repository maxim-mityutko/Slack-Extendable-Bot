from tweepy import Cursor, error
from common.cls.service import Connector
from common import logger

META = {
    'command': 'tw',
    'command_description': 'Retrieve Twitter feed.',
    'service': 'twitter',
    'slack_user_name': 'Twitter',
    'slack_icon_emoji': ':space_invader:',
    'slack_payload_type': 'text',
    'slack_payload_structure': {
        'text': '*Tweet:* {text}\n*Twitter URL:* <{service_url}|{service_url_wo_protocol}>'
    },
    'command_steps': {
        1: {
            'name': 'get_twitter_feed',
            'function_call': 'get_twitter_feed',
            'result_mapping': 'payload'
        },
    },
}

logger = logger.init(__name__)


def get_twitter_feed(connector: Connector, **kwargs):
    max_pages = 5  # One page is 20 tweets.
    tweet_url = 'https://twitter.com/{user_id}/status/{id}'
    try:

        if 'tweet_since_id' in kwargs and kwargs['tweet_since_id'] > 0:
            tweet_since_id = kwargs['tweet_since_id']
            logger.info('Previous session tweet id: {}'.format(tweet_since_id))
        else:
            tweet_since_id = connector.client.home_timeline(count=1)[0].id - 1
            logger.info('Latest tweet id: {}'.format(tweet_since_id))

        tweets = []
        for content in Cursor(connector.client.home_timeline, include_entities=False, since_id=tweet_since_id)\
                .pages(max_pages):
            for tweet in iter(content):
                tweets.append(
                    {
                        'id': tweet.id,
                        'text': tweet.text,
                        'user_id': tweet.user.id,
                        'user_name': tweet.user.screen_name,
                        'service_url': tweet_url.format(user_id=tweet.user.id, id=tweet.id)
                    }
                )

                # Update the 'tweet_since_id' value for the next session
                if tweet.id > tweet_since_id:
                    tweet_since_id = tweet.id

        logger.info('Overall tweets count: {0}'.format(len(tweets)))

        connector.config.misc = {'tweet_since_id': tweet_since_id}
        connector.config.set_misc()
        return tweets
    except error.RateLimitError as ex:
        logger.error('Code: {}, Message: {}'.format(ex['code'], ex['message']))

