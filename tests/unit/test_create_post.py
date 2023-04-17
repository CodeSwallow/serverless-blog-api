# import os
# import json
#
# import boto3
# import pytest
#
# from moto import mock_dynamodb
#
# from blog_api import create_post
#
#
# @pytest.fixture(scope="function")
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"
#     os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
#     os.environ['POSTS_TABLE'] = 'POSTS_TABLE'
#
#
# def test_initialization(aws_credentials):
#     event = {'body': '{ "title": "test" }'}
#     context = None
#
#     os.environ['POSTS_TABLE'] = ''
#
#     payload = create_post.create_post_handler(event, context)
#
#     assert payload['statusCode'] == 500
#
#
# @mock_dynamodb
# def test_missing_title(aws_credentials):
#     event = {'body': '{ "not_title": "test" }'}
#     context = None
#
#     payload = create_post.create_post_handler(event, context)
#
#     body = json.loads(payload['body'])
#
#     assert body['message'] == 'Title missing'
#
#
# @mock_dynamodb
# def test_valid_request(aws_credentials):
#     event = {
#         'body': '{"title": "Unit Testing"}',
#         'requestContext': {"authorizer": {"principalId": "test_user"}}
#     }
#     context = None
#
#     create_mock_ddb_table()
#
#     payload = create_post.create_post_handler(event, context)
#
#     assert payload['statusCode'] == 201
#
#
# @mock_dynamodb
# def create_mock_ddb_table():
#     mock_ddb = boto3.resource('dynamodb')
#     mock_ddb.create_table(
#         TableName='POSTS_TABLE',
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'PostID',
#                 'AttributeType': 'S'
#             },
#             {
#                 'AttributeName': 'Author',
#                 'AttributeType': 'S'
#             }
#         ],
#         KeySchema=[
#             {
#                 'AttributeName': 'PostID',
#                 'KeyType': 'HASH'
#             },
#             {
#                 'AttributeName': 'Author',
#                 'KeyType': 'RANGE'
#             }
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 123,
#             'WriteCapacityUnits': 123
#         }
#     )
