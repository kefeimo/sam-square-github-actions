[![sam-square-github-actions CI workflow](https://github.com/kefeimo/sam-square-github-actions/actions/workflows/square_workflow.yml/badge.svg)](https://github.com/kefeimo/sam-square-github-actions/actions/workflows/square_workflow.yml)
[![sam-square-github-actions CD workflow](https://github.com/kefeimo/sam-square-github-actions/actions/workflows/sam_workflow.yml/badge.svg?branch=main)](https://github.com/kefeimo/sam-square-github-actions/actions/workflows/sam_workflow.yml)

# sam-square-github-actions
sam-square-github-actions

# Tutorial: Deploy an AWS Serverless Application.

### Goal

Deploy an AWS serlerless application from local environment, using Serverless Application Model (SAM).

### Delivery

An AWS Lambda Function with public API—A microservice consist of Lambda Function and Amazon API Gateway.

### Steps

Stage0: Prerequisites

-   [ ] AWS account
-   [ ] Cloud9 environment
-   [ ] ssh credentials to Github (rsa public key)
-   [ ] setup virtualenv on Cloud9 (Python 3.7)
-   [ ] IAM credential for GitHub Action (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, configured for GitHub repo secrets)
-   [ ] Square API sandbox token (`SQUARE_TOKEN_TEST`, configured for GitHub repo secrets, exported as environment variable in Cloud9)

State1: Local Test

-   [ ] Clone the code from github to Cloud9.
    
    ```bash
    git clone git@github.com:XXXX
    
    ```
    
-   [ ] Activate the virtualenv (if is not up yet)
    
    ```bash
    source ${path-to-the-venv}/bin/activate
    
    ```
    
-   [ ] Install dependencies (including the local package) using Makefile
    
    ```bash
    make install
    
    ```
    
-   [ ] (Optional) Make some modification on the code.
    
-   [ ] Test using Makefile
    
    ```bash
    make test
    # optional
    make test_all
    
    ```
    
-   [ ] Run [demo.py](http://demo.py)
    
    ```bash
    python ${path-to-the-git-root-path}/squareup_api/demo/demo.py
    # assuming you are at the git-root-path
    python ./squareup_api/demo/demo.py
    
    ```
    

Stage2: Sam build and local test

-   [ ] Make sure you are at the git root path.
    
-   [ ] run `sam build`. (A `.aws-sam/build` directory should appear)
    
-   [ ] run sam locally
    
    ```bash
    sam local invoke
    
    ```
    
-   [ ] (optional) run [sam local start-api](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html)
    
    ```bash
    sam local start-api
    
    ```
    

Stage4: sam deploy

-   [ ] run sam deploy. (change `your-stack-name` as desired. change `us-east-2` as desired)
    
    ```bash
    
    sam deploy --no-confirm-changeset --no-fail-on-empty-changeset \
              --stack-name your-stack-name --resolve-s3 --capabilities CAPABILITY_IAM \
              --parameter-overrides SquareTokenTestRef=$SQUARE_TOKEN_TEST --region us-east-2
    
    
    ```
    

Stage5: verify and clean up.

-   [ ] Verify with `https://url-aws-assigned/your-api-endpoint`.
    
    <aside> 💡 Note: the `your-api-endpoint` is defined in `template.yaml`, Resources session, Events → Properties → path
    
    </aside>
    
-   [ ] Clearn up. (change `your-stack-name` as desired.)
    
    ```bash
    
    aws cloudformation delete-stack --stack-name your-stack-name
    
    
    ```
