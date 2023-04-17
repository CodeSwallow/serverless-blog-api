"""
Function to authorize the token and grant access to the API
"""
# TODO: Add the code to authorize the token and grant access to the API

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def token_authorizer_handler(event, context):
    """
    Authorizes the token and grants access to the API
    """

    logger.info("Event: {}".format(event))
    logger.info("Method ARN: {}".format(event['methodArn']))

    base_method_arn = event['methodArn'].split('/')[0]

    logger.info("Base method ARN: {}".format(base_method_arn))

    if event['authorizationToken'] == 'token':
        return generate_policy('user', 'Allow', base_method_arn + '/*/*')
    else:
        return generate_policy('user', 'Deny', base_method_arn + '/*/*')


def generate_policy(principal_id, effect, resource):
    """
    Generates the policy
    """
    auth_response = {'principalId': principal_id}

    if effect and resource:
        policy_document = {'Version': '2012-10-17', 'Statement': []}
        statement_one = {'Action': 'execute-api:Invoke', 'Effect': effect, 'Resource': resource}
        policy_document['Statement'].append(statement_one)
        auth_response['policyDocument'] = policy_document

    logger.info("Auth response: {}".format(auth_response))

    return auth_response
