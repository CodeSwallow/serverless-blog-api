"""
Lambda function to list posts
"""
# TODO: Add pagination
# TODO: Add filtering

import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def list_posts_handler(event, context):
    """
    Lists blog posts from DynamoDB
    """

    try:
        logger.info("Event: {}".format(event))

        table_name = os.getenv('POSTS_TABLE')
        if not table_name:
            raise Exception('Table name missing')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        items = table.scan()

        logger.info('DDB Response: {}'.format(items))

        if 'Items' in items:
            response = {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps(items['Items'])
            }
        else:
            response = {
                'statusCode': items['HTTPStatusCode'],
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
            "statusCode": 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            "body": {"message": 'Internal server error'}
        }
