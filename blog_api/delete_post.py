"""
Lambda function to delete a post from the database
"""
import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delete_post_handler(event, context):
    """
    Deletes a blog post from DynamoDB
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

        item = table.delete_item(
            Key={
                'PostID': post_id,
                'Author': event['requestContext']['authorizer']['principalId']
            }
        )

        logger.info('DDB Response: {}'.format(item))

        if 'Attributes' in item:
            response = {
                'statusCode': 204,
                'body': json.dumps(item['Attributes'])
            }
        else:
            response = {
                'statusCode': item['ResponseMetadata']['HTTPStatusCode']
            }

        logger.info("Response: %s", response)

        return response

    except Exception as error:
        logger.info('Error: {}'.format(error))

        return {
            "statusCode": 500,
            "body": {"message": 'Internal server error'}
        }
