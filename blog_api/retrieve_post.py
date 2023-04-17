"""
Lambda function to get a post from the database
"""
import os
import json
import logging
import datetime

import boto3
from slugify import slugify

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def retrieve_post_handler(event, context):
    """
    Retrieves a blog post from DynamoDB
    """

    try:
        logger.info("Event: {}".format(event))

        table_name = os.getenv('POSTS_TABLE')
        if not table_name:
            raise Exception('Table name missing')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        try:
            post_id = event['pathParameters']['slug']
        except KeyError as error:
            logger.info('Error: {}'.format(error))

            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        item = table.query(
            KeyConditionExpression='PostID = :post_id',
            ExpressionAttributeValues={
                ':post_id': post_id
            }
        )

        logger.info('DDB Response: {}'.format(item))

        if 'Items' in item:
            response = {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps(item['Items'])
            }
        else:
            response = {
                'statusCode': item['ResponseMetadata']['HTTPStatusCode'],
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
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
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            "body": {"message": 'Internal server error'}
        }
