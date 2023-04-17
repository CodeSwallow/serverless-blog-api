import os
import json

import boto3
import pytest

from moto import mock_dynamodb

from blog_api import list_posts

# TODO: Add pagination tests
# TODO: Add filtering tests


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ['POSTS_TABLE'] = 'POSTS_TABLE'


def test_initialization(aws_credentials):
    event = {}
    context = None

    os.environ['POSTS_TABLE'] = ''

    payload = list_posts.list_posts_handler(event, context)

    assert payload['statusCode'] == 500


@mock_dynamodb
def test_empty_table(aws_credentials):
    event = {}
    context = None

    create_mock_ddb_table()

    payload = list_posts.list_posts_handler(event, context)

    assert json.loads(payload['body']) == []


@mock_dynamodb
def test_valid_request(aws_credentials):
    event = {}
    context = None

    table = create_mock_ddb_table()
    table.put_item(
        Item={
            'PostID': 'a7a3ac1eb24d4aa68ac64e49bb09f1d2',
            'Slug': 'unit-testing',
            'Title': 'Unit Testing',
            'Content': 'Unit Testing Content',
            'Author': 'test_user'
        }
    )

    payload = list_posts.list_posts_handler(event, context)

    assert payload['statusCode'] == 200


@mock_dynamodb
def create_mock_ddb_table():
    mock_ddb = boto3.resource('dynamodb')
    mock_ddb.create_table(
        TableName='POSTS_TABLE',
        AttributeDefinitions=[
            {
                'AttributeName': 'PostID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Author',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'PostID',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Author',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 123,
            'WriteCapacityUnits': 123
        }
    )
    return mock_ddb.Table('POSTS_TABLE')

