import os
import slack

import sys
sys.path.append('./')  # Expose parent level of project in order to be able to import 'core' and 'common' modules.

from core import environment, command, service
from common import logger


def send_message(web_client: slack.WebClient, channel: str, payload: list, **kwargs):
    if payload:
        for item in payload:
            # TODO: Rate limit 20 messages per minute max
            result = web_client.chat_postMessage(
                channel=channel,
                text=item['text'] if 'text' in item else None,
                blocks=item['blocks'] if 'blocks' in item else None,
                username=item['username'] if 'username' in item else DEFAULT_FRIENDLY_NAME,
                icon_emoji=item['icon_emoji'] if 'icon_emoji' in item else DEFAULT_ICON_EMOJI,
                unfurl_links=True,
            )
            if result['ok']:
                logger.info('Message sent to Slack channel {}.'.format(channel))
            else:
                logger.error('Error sending to Slack channel {}, reason: {}'.format(channel, result['error']))


@slack.RTMClient.run_on(event='message')
def on_message(**kwargs):
    wc = kwargs['web_client']
    bot_id = wc.api_call("auth.test")["user_id"]
    channel = kwargs['data']['channel']
    if 'subtype' not in kwargs['data'] and bot_id in kwargs['data']['text']:
        # Check if user sent a valid command.
        send_message(
            web_client=wc,
            channel=channel,
            payload=command.get_payload(
                connectors=connectors,
                payloads=payloads,
                command=kwargs['data']['text'],
                user=kwargs['data']['user']
            ),
        )


@slack.RTMClient.run_on(event='hello')
def on_connect(**kwargs):
    logger.info("Slack bot connected and running...")
    wc = kwargs['web_client']
    logger.info('Trigger: HELLO')
    '''
    send_message(
        web_client=wc,
        channel=DEFAULT_SLACK_CHANNEL,
        payload=cc.get_payload(commands['dr']),
    )
    '''


@slack.RTMClient.run_on(event='goodbye')
def on_disconnect(**kwargs):
    logger.warning("Slack bot disconnecting...")


if __name__ == "__main__":
    environment.configure()

    DEFAULT_SLACK_CHANNEL = os.environ.get('DEFAULT_SLACK_CHANNEL')
    DEFAULT_FRIENDLY_NAME = os.environ.get('DEFAULT_FRIENDLY_NAME')
    DEFAULT_ICON_EMOJI = os.environ.get('DEFAULT_ICON_EMOJI')
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

    # TODO: async execution
    # TODO: Slow down send message rate to avoid 'rate limited' error from Slack
    # Instantiate Slack client
    slack_client = slack.RTMClient(token=SLACK_BOT_TOKEN)

    logger = logger.init(__name__)
    logger.warning('Bot initializing...')

    # Load all available 'connectors' and 'payloads'
    connectors = service.get_connectors_meta()
    payloads = service.get_payloads_meta()

    slack_client.start()
