# GitHub Actions - Push Docker Image to AWS ECR

This repository demonstrates how to push a Docker Image to AWS ECR using GitHub Actions.

## 1. OpenID Connect (OIDC) Identity Provider

To authenticate with AWS from GitHub Actions, you need to create an OIDC Identity Provider in AWS IAM. This Identity Provider will be used to generate temporary credentials for GitHub Actions.

1. Go to `AWS IAM Console`
2. Go to `Identity providers` from left menu
3. Click on `Add provider` button
4. Select `OpenID Connect` as provider type, type `https://token.actions.githubusercontent.com` in provider URL field and click on `Get thumbprint` button, type `sts.amazonaws.com` in Audience field, and click on `Add provider` button


## 2. Create ECR Repository

Create a private ECR repository from AWS console.

## 3. Create IAM Role

1. Go to `AWS IAM Console`
2. Go to `Roles` from left menu
3. Click on `Create role` button
4. Select `Custom trust policy` and edit the JSON like below

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::<AWS account ID>:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:<GitHub User>/<GitHub Repo>:ref:refs/heads/<branch>"
                }
            }
        }
    ]
}
```

5. Attach policies with custom inline policies
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "ecr:GetAuthorizationToken",
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Action": [
                "ecr:UploadLayerPart",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:CompleteLayerUpload",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Effect": "Allow",
            "Resource": "<ARN of ECR repository>"
        }
    ]
}
```


## 4. Create a Dockerfile

From the github repository, create a Dockerfile with the following content:

```Dockerfile
FROM alpine:3
```

If you have any Dockerfile you want to use, you can use that as well.

## 5. Create GitHub Actions Workflow

In `.github/workflows` directory, create a new workflow file with the following content:

```
name: ecr push image

on:
  push:

jobs:
  push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v3

      # AWS authentication
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-region: "<AWS region>"
          role-to-assume: "<ARN of IAM role for GitHub Actions>"

      # ECR login
      - uses: aws-actions/amazon-ecr-login@v1
        id: login-ecr

      # build docker image and push to ecr
      - name: build and push docker image to ecr
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          REPOSITORY: "<ECR repository name>"
          IMAGE_TAG: ${{ github.sha }} # this could be any tag you want like "latest
        run: |
          docker build . --tag ${{ env.REGISTRY }}/${{ env.REPOSITORY }}:${{ env.IMAGE_TAG }}
          docker push ${{ env.REGISTRY }}/${{ env.REPOSITORY }}:${{ env.IMAGE_TAG }}
```
