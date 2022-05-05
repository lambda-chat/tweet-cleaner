# Deployment with AWS-CDK

Commands are valid in `cdk/` directory.

```sh
cd cdk
```

## Development with TypeScript

### Install JavaScript packages

```sh
npm ci
```

### .env settings

`.env` will be moved to the Lambda function environment). The contents are like below.

```txt
ENCRYPTED_ACCESS_TOKEN_SECRET__OWNER=...
ENCRYPTED_ACCESS_TOKEN_SECRET__USER1=...
ENCRYPTED_ACCESS_TOKEN__OWNER=...
ENCRYPTED_ACCESS_TOKEN__USER1=...
ENCRYPTED_API_KEY=...
ENCRYPTED_API_SECRET_KEY=...
USER_CONFIG_KEYS="OWNER,USER1"
OWNER=...
USER1=...
LAMBDA_API_KEY=...
```

## Deploy and Destroy

### Deploy

```sh
cdk bootstrap    # if first deploy by the account or on the region
./pre-deploy.sh  # prepare python packages for Lambda layer
cdk deploy
```

### Destroy

```sh
cdk destroy
```
