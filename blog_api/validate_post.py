import os
import json
import logging
import datetime
import uuid

import boto3
from slugify import slugify

logger = logging.getLogger()
logger.setLevel(logging.INFO)

step_functions = boto3.client('stepfunctions')


def validate_post_handler(event, context):
    try:
        logger.info("Event: {}".format(event))
        logger.info("Context: {}".format(context))

        try:
            payload = json.loads(event['body'])
        except KeyError as error:
            logger.info('Error: {}'.format(error))

            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        if 'title' not in payload or 'content' not in payload:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing title or content field'})
            }

        state_machine_arn = os.getenv('STATE_MACHINE')
        if not state_machine_arn:
            raise Exception('State machine ARN missing')

        logger.info('State Machine ARN: {}'.format(state_machine_arn))

        description = '' if 'description' not in payload else payload['description']
        tags = [] if 'tags' not in payload else payload['tags']

        post = {
            'post_id': uuid.uuid4().hex,
            'title': payload['title'],
            'slug': slugify(payload['title']),
            'description': description,
            'author': event['requestContext']['authorizer']['principalId'],
            'content': payload['content'],
            'date_created': datetime.datetime.now().isoformat(),
            'date_updated': datetime.datetime.now().isoformat(),
            'tags': tags,
        }

        logger.info('Post: {}'.format(post))

        res = step_functions.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(post)
        )

        logger.info('Step Functions Response: {}'.format(res))

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Post is valid'})
        }

    except Exception as error:
        logger.info('Error: {}'.format(error))

        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': 'Internal server error'
        }
