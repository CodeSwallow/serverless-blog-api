"""
Lambda function to update a post in the database
"""
import os
import json
import logging
import datetime

import boto3
from slugify import slugify

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_post_handler(event, context):
    """
    Updates a blog post in DynamoDB
    """

    try:
        logger.info("Event: {}".format(event))

        table_name = os.getenv('POSTS_TABLE')
        if not table_name:
            raise Exception('Table name missing')

        try:
            post_id = event['pathParameters']['slug']
        except KeyError as error:
            logger.info('Error: {}'.format(error))

            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        try:
            payload = json.loads(event['body'])
        except KeyError as error:
            logger.info('Error: {}'.format(error))

            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        if 'title' not in payload and 'content' not in payload and 'description' not in payload and 'tags' not in payload:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No fields to update'})
            }

        item = table.update_item(
            Key={
                'PostID': post_id,
                'Author': event['requestContext']['authorizer']['principalId']
            },
            UpdateExpression=build_update_expression(payload),
            ExpressionAttributeValues=build_attribute_values(payload),
            ReturnValues='ALL_NEW'
        )

        logger.info('DDB Response: {}'.format(item))

        if 'Attributes' in item:
            response = {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,PUT'
                },
                'body': json.dumps(item['Attributes'])
            }
        else:
            response = {
                'statusCode': item['ResponseMetadata']['HTTPStatusCode'],
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,PUT'
                },
            }

        logger.info("Response: %s", response)

        return response

    except Exception as error:
        logger.info('Error: {}'.format(error))

        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,PUT'
            },
            "body": {"message": "Internal Server Error"}
        }


def build_update_expression(payload):
    update_expression = 'set '

    if 'title' in payload:
        update_expression += 'Title = :t, Slug = :s, '
    if 'content' in payload:
        update_expression += 'Content = :c, '
    if 'description' in payload:
        update_expression += 'Description = :d, '
    if 'tags' in payload:
        update_expression += 'Tags = :t, '

    logger.info('Update Expression: {}'.format(update_expression[:-2]))

    return update_expression[:-2]


def build_attribute_values(payload):
    attributes = {}

    if 'title' in payload:
        attributes[':t'] = payload['title']
        attributes[':s'] = slugify(payload['title'])
    if 'content' in payload:
        attributes[':c'] = payload['content']
    if 'description' in payload:
        attributes[':d'] = payload['description']
    if 'tags' in payload:
        attributes[':t'] = payload['tags']

    logger.info('Attributes: {}'.format(attributes))

    return attributes
