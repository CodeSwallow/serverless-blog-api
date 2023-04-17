"""
Lambda function used for post creation SNS topic
"""
import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def post_creation_topic_handler(event, context):
    """
    Handles post creation SNS topic
    """
    try:
        logger.info("Event: {}".format(event))

        sns_client = boto3.client('sns')
        topic_arn = os.getenv('TOPIC_ARN')

        logger.info('Topic ARN: {}'.format(topic_arn))

        if 'Records' in event:
            for record in event['Records']:
                message = record['Sns']['Message']
                message_id = record['Sns']['MessageId']
                subject = record['Sns']['Subject']
                timestamp = record['Sns']['Timestamp']

                print('Received SNS message:')
                print('Message ID:', message_id)
                print('Subject:', subject)
                print('Timestamp:', timestamp)
                print('Message:', message)

            return {
                'statusCode': 200,
                'body': 'Event handled successfully.'
            }

        if 'body' in event:
            payload = json.loads(event['body'])
            if payload['Type'] == 'SubscriptionConfirmation':
                response = sns_client.confirm_subscription(
                    TopicArn=topic_arn,
                    Token=payload['Token'],
                    AuthenticateOnUnsubscribe='true'
                )

                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print('Subscription confirmed successfully.')
                else:
                    print('Failed to confirm subscription:', response)

                return {
                    'statusCode': 200,
                    'body': 'Subscription confirmation handled successfully.'
                }

    except Exception as error:
        logger.info('Error: {}'.format(error))
        raise error
