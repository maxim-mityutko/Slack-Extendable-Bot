from common import aws
import pickle
from base64 import b64encode, b64decode
import json


class UserServiceConfig(object):
    def __init__(self,  service: str, user: str):
        self.user = user
        self.service = service
        self.oauth_token = None
        self.oauth_token_secret = None
        self.misc = None

    def get_config(self):
        resource = aws.resource('dynamodb')
        params = {
            'Table': 'user_service',
            'Key': {'user': self.user, 'service': self.service}
        }
        response = aws.dynamodb_get_item(resource, params)
        if response:
            self.oauth_token = response['oauth']['token']
            self.oauth_token_secret = response['oauth']['token_secret']
            self.misc = response['misc'] if 'misc' in response else {}

        # logger.warning('Module \'{0}\' credentials do not exist.'.format(connector_name))

    def set_oauth(self):
        res = aws.resource('dynamodb')
        params = {
            'Table': 'user_service',
            'Key': {'user': self.user, 'service': self.service},
            'UpdateExpression': 'set #o = :o, #m = :m',
            'ExpressionAttributeNames': {'#o': 'oauth', '#m': 'misc'},
            'ExpressionAttributeValues': {
                ':o': {'token': self.oauth_token, 'token_secret': self.oauth_token_secret},
                ':m': {}
            }
        }
        aws.dynamodb_update_item(
            resource=res,
            params=params
        )

    def set_misc(self):
        res = aws.resource('dynamodb')
        params = {
            'Table': 'user_service',
            'Key': {'user': self.user, 'service': self.service},
            'UpdateExpression': 'set #m = :m',
            'ExpressionAttributeNames': {'#m': 'misc'},
            'ExpressionAttributeValues': {':m': self.misc}
        }
        aws.dynamodb_update_item(
            resource=res,
            params=params
        )


class UserServiceAuthState(object):
    def __init__(self, user: str, service: str):
        self.user = user
        self.service = service
        self.oaw = None

    def get_oaw(self):
        resource = aws.resource('dynamodb')
        params = {
            'Table': '_oauth_wrapper_state',
            'Key': {'user': self.user, 'service': self.service}
        }
        response = aws.dynamodb_get_item(resource, params)
        self.oaw = pickle.loads(b64decode(response['state'].value))

        return True

    def set_oaw(self):
        res = aws.resource('dynamodb')
        params = {
            'Table': '_oauth_wrapper_state',
            'Key': {'user': self.user, 'service': self.service},
            'UpdateExpression': 'set #st = :st, #sv = :sv, #t = :t',
            'ExpressionAttributeNames': {'#st': 'state', '#sv': 'service', '#t': 'token'},
            'ExpressionAttributeValues': {
                ':st': b64encode(pickle.dumps(self.oaw)),
                ':sv': self.oaw.connector_name,
                ':t': self.oaw.oauth_token,
            }
        }
        aws.dynamodb_update_item(
            resource=res,
            params=params
        )

        return True

    def del_oaw(self):
        res = aws.resource('dynamodb')
        params = {
            'Table': '_oauth_wrapper_state',
            'Key': {'user': self.user, 'service': self.service},
        }
        aws.dynamodb_delete_item(
            resource=res,
            params=params
        )


class User(object):
    def __init__(self):
        self.user = None
        self.name = None
        self.team = None
        self.access_token = None
        self.scope = None
        self.service = []

    def set_user(self, identity: str):
        res = aws.resource('dynamodb')
        identity = json.loads(identity)
        self.user = identity['user_id']
        self.name = identity['user']['name']
        self.team = identity['team_id']
        self.access_token = identity['access_token']
        self.scope = identity['scope']

        params = {
            'Table': 'user',
            'Key': {'user': self.user},
            'UpdateExpression': 'set #at = :at, #s = :s, #t = :t, #n = :n',
            'ExpressionAttributeNames': {
                '#at': 'access_token',
                '#s': 'scope',
                '#t': 'team',
                '#n': 'name',
            },
            'ExpressionAttributeValues': {
                ':at': self.access_token,
                ':s': self.scope,
                ':t': self.team,
                ':n': self.name,
            }
        }

        aws.dynamodb_update_item(
            resource=res,
            params=params
        )

    def get_user(self, user: str):
        res = aws.resource('dynamodb')
        params = {
            'Table': 'user',
            'Key': {'user': user},
        }
        response = aws.dynamodb_get_item(resource=res, params=params)
        if response:
            self.user = response['user']
            self.name = response['name']
            self.team = response['team']
            self.access_token = response['access_token']
            self.scope = response['scope']
        params = {
            'Table': 'user_service',
            'KeyConditionExpression': '#u = :u',
            'ExpressionAttributeNames': {'#u': 'user'},
            'ExpressionAttributeValues': {':u': user}
        }
        response = aws.dynamodb_query(resource=res, params=params)
        if response:
            for item in response:
                usc = UserServiceConfig(user=item['user'], service=item['service'])
                usc.oauth_token = item['oauth']['token']
                usc.oauth_token_secret = item['oauth']['token_secret']
                usc.misc = item['misc']
                self.service.append(usc)
