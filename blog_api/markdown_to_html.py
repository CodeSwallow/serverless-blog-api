"""
Lambda function to convert Markdown to HTML and upload to S3
"""
import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def markdown_to_html_handler(event, context):
    """
    Converts Markdown to HTML and uploads to S3
    """
    try:
        logger.info("Event: {}".format(event))

        bucket_name = os.getenv('POSTS_BUCKET')
        if not bucket_name:
            raise Exception('Bucket name missing')

        logger.info('Table name: {}'.format(bucket_name))

        s3 = boto3.client('s3')

        content = event['sanitized_html']

        logger.info('Content: {}'.format(content))

        file_name = event['author'] + '/' + event['slug'] + '.html'

        res = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=content.encode('utf-8'),
            ContentType='text/html',
            ACL='public-read'
        )

        logger.info('S3 Response: {}'.format(res))

        ddb = boto3.resource('dynamodb')
        ddb_table = ddb.Table(os.getenv('POSTS_TABLE'))

        res = ddb_table.put_item(
            Item={
                'PostID': event['post_id'],
                'Title': event['title'],
                'Slug': event['slug'],
                'Description': event['description'],
                'Author': event['author'],
                'Content': event['content'],
                'DateCreated': event['date_created'],
                'DateUpdated': event['date_updated'],
                'Tags': event['tags'],
                'HtmlURL': f'https://{bucket_name}.s3.amazonaws.com/{file_name}'
            }
        )

        logger.info('DDB Response: {}'.format(res))

    except Exception as error:
        logger.info('Error: {}'.format(error))
        raise error
