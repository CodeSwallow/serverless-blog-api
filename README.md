# serverless-blog

Serverless REST API with AWS Lambda, API Gateway, DynamoDB, and Python for a blog

Swagger API: https://irs-test-bucket.s3.amazonaws.com/swagger.html
![Swagger Image](https://irs-test-bucket.s3.amazonaws.com/swagger_image.png)

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
serverless-blog$ sam build --use-container
```

The SAM CLI installs dependencies defined in `hello_world/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
serverless-blog$ sam local invoke ListPostFunction --event events/list_event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
serverless-blog$ sam local start-api
serverless-blog$ curl http://localhost:3000/
```

## Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
serverless-blog$ pip install -r tests/requirements.txt --user
# unit test
serverless-blog$ python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
serverless-blog$ AWS_SAM_STACK_NAME=<stack-name> python -m pytest tests/integration -v
```
