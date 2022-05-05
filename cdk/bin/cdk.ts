#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { LambdaStack } from "../lib/lambda-stack";

const app = new cdk.App();
const lambdaStack = new LambdaStack(app, "LambdaStack");

export default lambdaStack;
