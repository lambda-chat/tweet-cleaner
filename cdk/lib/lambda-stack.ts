import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as iam from 'aws-cdk-lib/aws-iam';

const environment: { [key: string]: string } = require('dotenv').config().parsed;

export class LambdaStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const lambdaLayer = new lambda.LayerVersion(this, 'python_packages', {
      code: lambda.Code.fromAsset(path.join(__dirname, "..", "python_packages")),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_9],
      description: "Python Packages",
    });

    const lambdaFn = new lambda.Function(this, 'TweetCleanerFunction', {
      functionName: 'tweet-cleaner',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'app.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, "..", "..", "lambda")),
      timeout: cdk.Duration.seconds(180),
      retryAttempts: 1,
      environment: environment,
      layers: [lambdaLayer],
    });

    lambdaFn.addToRolePolicy(new iam.PolicyStatement(
      {
        effect: iam.Effect.ALLOW,
        actions: ['kms:Decrypt'],
        resources: ["*"],
      }
    ));

    const key = kms.Alias.fromAliasName(this, 'kmsKey', 'removeOldTweetsKey');
    key.grantDecrypt(lambdaFn);

    const rule = new events.Rule(this, 'EveryJST1amEvent', {
      schedule: events.Schedule.expression('cron(0 8 * * ? *)'),
    });
    rule.addTarget(new targets.LambdaFunction(lambdaFn));
  }
}
