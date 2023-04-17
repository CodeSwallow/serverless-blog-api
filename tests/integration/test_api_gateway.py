import os
import uuid

import boto3
import pytest
import requests

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway:

    @pytest.fixture(scope="class")
    def api_gateway_url(self):
        """ Get the API Gateway URL from Cloudformation Stack outputs """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ServerlessRestApi"]

        if not api_outputs:
            raise KeyError(f"ServerlessRestApi not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"] + "/posts"

    @pytest.fixture(scope="class")
    def ddb_item_id(self):
        """ Create an Item in DynamoDB """

        ddb_table_name = os.environ.get("POSTS_TABLE")
        ddb = boto3.resource("dynamodb")
        table = ddb.Table(ddb_table_name)

        post_id = uuid.uuid4().hex

        table.put_item(
            Item={
                "PostID": post_id,
                "Slug": "integration-tests",
                "Title": "Integration Tests",
                "Content": "test_content",
                "Author": "user",
                "DateCreated": "2020-01-01T00:00:00.000000",
                "Description": "test_description",
                "Tags": [],
            }
        )

        return post_id

    def test_list_posts(self, api_gateway_url):
        """ Call the API Gateway endpoint using GET Method """
        response = requests.get(api_gateway_url)

        assert response.status_code == 200
        assert isinstance(response.json(), list) is True

    # def test_create_post(self, api_gateway_url):
    #     """ Call the API Gateway endpoint using POST Method """
    #     response = requests.post(api_gateway_url, json={"title": "Create Post Test"}, headers={"Authorization": "token"})
    #
    #     assert response.status_code == 201
    #     assert isinstance(response.json(), dict) is True
    #     assert response.json().get("Title") == "Create Post Test"

    def test_get_post(self, api_gateway_url, ddb_item_id):
        """ Call the API Gateway endpoint using GET Method """
        post_id = ddb_item_id
        response = requests.get(f'{api_gateway_url}/{post_id}')

        assert response.status_code == 200
        assert isinstance(response.json(), list) is True
        assert response.json()[0].get("Title") == "Integration Tests"

    def test_update_post(self, api_gateway_url, ddb_item_id):
        """ Call the API Gateway endpoint using PUT Method """
        post_id = ddb_item_id
        response = requests.put(f'{api_gateway_url}/{post_id}', json={"title": "UPDATED Integration Test"}, headers={"Authorization": "token"})

        assert response.status_code == 200
        assert isinstance(response.json(), dict) is True
        assert response.json().get("Title") == "UPDATED Integration Test"

    def test_delete_post(self, api_gateway_url, ddb_item_id):
        """ Call the API Gateway endpoint using DELETE Method """
        post_id = ddb_item_id
        response = requests.delete(f'{api_gateway_url}/{post_id}', headers={"Authorization": "token"})

        assert response.status_code == 200
