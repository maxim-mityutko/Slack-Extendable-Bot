import boto3
from botocore.exceptions import ClientError
from os import environ as env
import json

from common import logger

logger = logger.init(__name__)


def resource(service: str) -> boto3.resource:
    return boto3.resource(service,
                          region_name=env.get('AWS_REGION_NAME'),
                          aws_access_key_id=env.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=env.get('AWS_SECRET_ACCESS_KEY'),
                          )


def dynamodb_get_item(resource: boto3.resource, params: dict) -> json:
    table = resource.Table(params['Table'])
    try:
        response = table.get_item(Key=params['Key'])
    except ClientError as ex:
        logger.error(ex.response['Error']['Message'])
    else:
        if 'Item' in response:
            return response['Item']  # Record exists.
        else:
            return None  # Record does not exist.


# UpdateItem will update existing key values and create new keys/records in the table.
def dynamodb_update_item(resource: boto3.resource, params: dict) -> bool:
    table = resource.Table(params['Table'])
    try:
        response = table.update_item(
            Key=params['Key'],
            UpdateExpression=params['UpdateExpression'],
            ExpressionAttributeNames=params['ExpressionAttributeNames'],
            ExpressionAttributeValues=params['ExpressionAttributeValues'],
        )
    except ClientError as ex:
        logger.error(ex.response['Error']['Message'])
    else:
        logger.info('DynamoDb key \'{key}\' in \'{table}\' table has been updated.'
                    .format(key=str(params['Key']), table=params['Table']))
        return True


def dynamodb_delete_item(resource: boto3.resource, params: dict) -> bool:
    table = resource.Table(params['Table'])
    try:
        table.delete_item(
            Key=params['Key']
        )
    except ClientError as ex:
        logger.error(ex.response['Error']['Message'])
    else:
        logger.info('DynamoDb key \'{key}\' in \'{table}\' table has been deleted.'
                    .format(key=str(params['Key']), table=params['Table']))
        return True


def dynamodb_scan(resource: boto3.resource, params: dict) -> json:
    table = resource.Table(params['Table'])
    try:
        response = table.scan()
    except ClientError as ex:
        logger.error(ex.response['Error']['Message'])
    else:
        if 'Items' in response:
            logger.info('DynamoDb table \'{table}\' returned {len} items.'
                        .format(table=params['Table'], len=len(response['Items'])))
            return response['Items']


def dynamodb_query(resource: boto3.resource, params: dict) -> json:
    table = resource.Table(params['Table'])
    try:
        response = table.query(
            KeyConditionExpression=params['KeyConditionExpression'],
            ExpressionAttributeNames=params['ExpressionAttributeNames'],
            ExpressionAttributeValues=params['ExpressionAttributeValues'],
        )
    except ClientError as ex:
        logger.error(ex.response['Error']['Message'])
    else:
        if 'Items' in response:
            logger.info('DynamoDb table \'{table}\' returned {len} items.'
                        .format(table=params['Table'], len=len(response['Items'])))
            return response['Items']
