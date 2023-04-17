"""
Lambda function to process image and upload to S3
"""
import os
import io
import json
import uuid
import base64
import logging

import boto3

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def upload_image_handler(event, context):
    """
    Processes an image and uploads it to S3
    """
    try:
        logger.info("Event: {}".format(event))

        parser = StreamingFormDataParser(headers=event['headers'])

        image_target = ValueTarget()
        parser.register('image', image_target)
        image_data = base64.b64decode(event['body'])
        parser.data_received(image_data)

        if not validate_image(image_target.value):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid image'})
            }

        object_key = event['requestContext']['authorizer']['principalId'] + '/' + uuid.uuid4().hex + '.jpg'
        bucket_name = os.getenv('POSTS_BUCKET')
        if not bucket_name:
            raise Exception('Bucket name missing')

        logger.info("Object key: %s", object_key)
        logger.info("Bucket name: %s", bucket_name)

        s3_resource = boto3.resource('s3')
        s3_file = s3_resource.Object(bucket_name, object_key)
        s3_file.put(Body=image_target.value, ACL='public-read', ContentType='image/jpeg')

        image_url = f'https://{bucket_name}.s3.amazonaws.com/{object_key}'

        logger.info("Image URL: %s", image_url)

        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'url': image_url})
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
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def validate_image(image_data):
    """
    Validates the image data
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            raise Exception('Invalid image format')

        max_size = 4 * 1024 * 1024  # 4MB
        if len(image_data) > max_size:
            return False

        image.verify()
        image.close()

        return True

    except Exception as e:
        logger.info('Error: {}'.format(e))
        return False


# TODO: Add a test for this function
