import json

import pytest

from blog_api import token_authorizer

# TODO: Add the code to test the token_authorizer_handler function


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "type": "TOKEN",
        "authorizationToken": "token",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:123456789/dev/GET/posts"
    }


def test_lambda_handler(apigw_event):
    res = token_authorizer.token_authorizer_handler(apigw_event, "")
    data = res["policyDocument"]

    assert data["Version"] == "2012-10-17"
    assert "Action" in data["Statement"][0]
    assert data["Statement"][0]["Action"] == "execute-api:Invoke"

