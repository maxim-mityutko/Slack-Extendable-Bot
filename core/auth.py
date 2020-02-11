import pkgutil
import importlib

from os import environ as env
from typing import Optional

from common import logger
from common.oauther import OAuthWrapper
from common.cls.user import UserServiceAuthState, UserServiceConfig, User

# Package containing all the modules for import
from service import connector

logger = logger.init(__name__)


def start_auth(connector: dict, user: str):
    oaw = OAuthWrapper(
        consumer_key=connector['consumer_key'],
        consumer_secret=connector['consumer_secret'],
        request_token_url=connector['endpoints']['request_token'],
        authorize_url=connector['endpoints']['authorize'],
        access_token_url=connector['endpoints']['access_token'],
        user_agent=env['USER_AGENT'],
        callback_uri='{url}/service-callback'.format(url=env['CALLBACK_URI']),
        connector_name=connector['service'],
    )
    url = oaw.get_authorization_url()
    save_oauthwrapper(oaw=oaw, user=user)
    return url


def save_oauthwrapper(oaw: OAuthWrapper, user: str):
    state = UserServiceAuthState(user=user)
    state.oaw = oaw
    return state.set_oaw()


def restore_oauthwrapper(user: str, service: str) -> OAuthWrapper:
    state = UserServiceAuthState(user=user, service=service)
    state.get_oaw()
    oaw = state.oaw
    state.del_oaw()  # After OAuthWrapper object has been restored, there is no need to keep it in database.
    return oaw


def finish_auth(oauth_token: str, verifier: str, code: str, user: str, service: str):
    oaw = restore_oauthwrapper(user=user, service=service)
    oaw.oauth_verifier = verifier if verifier is not None else code
    oaw.oauth_token = oauth_token
    if oaw.get_access_token():
        conf = UserServiceConfig(service=oaw.connector_name, user=user)
        conf.oauth_token = oaw.oauth_token
        conf.oauth_token_secret = oaw.oauth_token_secret
        conf.set_oauth()
        return True


def get_config(service: str, user: str) -> Optional[UserServiceConfig]:
    conf = UserServiceConfig(service=service, user=user)
    conf.get_config()
    if conf.oauth_token is not None and conf.oauth_token_secret is not None:
        return conf
    else:
        return None


def set_user_identity(oauth_response: str) -> User:
    """
    :param oauth_response: Identity response from Slack user authentication service.
    :return: User object holding Slack identity information.
    """
    user = User()
    user.set_user(oauth_response)
    return user


def get_user_identity(user: str) -> User:
    """
    :param user: Authenticated Slack user.
    :return: User object holding Slack identity information and authorized services (User; UserServiceConfig).
    """
    usr = User()
    usr.get_user(user=user)
    return usr
