import os
import json

import boto3
import pytest

from moto import mock_dynamodb

from blog_api import delete_post


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

    payload = delete_post.delete_post_handler(event, context)

    assert payload['statusCode'] == 500


def test_missing_path_parameter(aws_credentials):
    event = {'pathParameters': {}}
    context = None

    payload = delete_post.delete_post_handler(event, context)

    assert payload['statusCode'] == 400


@mock_dynamodb
def test_valid_request(aws_credentials):
    event = {
        'pathParameters': {'slug': 'a7a3ac1eb24d4aa68ac64e49bb09f1d2'},
        'requestContext': {"authorizer": {"principalId": "test_user"}}
    }
    context = None

    create_mock_ddb_table()

    payload = delete_post.delete_post_handler(event, context)

    assert payload['statusCode'] == 204


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
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    mock_ddb.Table('POSTS_TABLE').put_item(
        Item={
            'PostID': 'a7a3ac1eb24d4aa68ac64e49bb09f1d2',
            'Slug': 'unit-testing',
            'Title': 'Unit Testing',
            'Content': 'Unit Testing Content',
            'Author': 'test_user'
        }
    )
