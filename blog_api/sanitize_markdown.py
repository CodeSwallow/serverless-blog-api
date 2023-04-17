"""
Lambda function to sanitize markdown
"""
import os
import json
import logging

from functools import partial

import boto3
import markdown
from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def sanitize_markdown_handler(event, context):
    """
    Sanitizes markdown
    """
    try:
        logger.info("Event: {}".format(event))

        markdown_content = event['content']

        logger.info('Markdown Content: {}'.format(markdown_content))

        try:
            html_content = markdown.markdown(markdown_content)
        except Exception as error:
            logger.info('Error: {}'.format(error))
            raise error

        logger.info('HTML Content: {}'.format(html_content))

        cleaner = Cleaner(tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em',
                                'a', 'img', 'blockquote', 'pre', 'code', 'hr', 'br'],
                          attributes={'a': ['href', 'title'], 'img': ['src', 'alt']},
                          strip=True,
                          filters=[partial(LinkifyFilter, skip_tags=['pre', 'code'])])

        sanitized_html = cleaner.clean(html_content)

        logger.info('Sanitized HTML: {}'.format(sanitized_html))

        event['sanitized_html'] = sanitized_html

        logger.info('Event: {}'.format(event))

        return event

    except Exception as error:
        logger.info('Error: {}'.format(error))
        raise error
