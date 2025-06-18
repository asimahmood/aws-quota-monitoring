# AWS Quota Monitoring System

This repository implements a complete AWS quota monitoring and alerting system using:
- Lambda functions
- Layers
- Step Functions
- EventBridge Scheduler (runs daily)

## 🧱 Project Structure

```
aws-quota-monitoring/
├── lambdas/
│   ├── quota_checker/
│   │   └── lambda_function.py
│   └── merge_results/
│       └── lambda_function.py
├── layers/
│   └── quota_checker_layer/
│       └── python/   # site-packages
├── step_function/
│   └── state_machine_definition.json
└── README.md
```

## 🚀 How to Use

### 1. Deploy Lambda Layers
Upload the `layers/quota_checker_layer/` as a ZIP to create a Lambda Layer with:
- `aws_quota`, `boto3`, `click`, etc.

### 2. Deploy Lambdas
- `QuotaCheckerLambda`: contains `lambda_function.py` for individual quota checks.
- `QuotaMergeLambda`: combines batch results to one.

### 3. Create Step Function
Use `step_function/state_machine_definition.json` to deploy the full Step Function.

### 4. Schedule with EventBridge
Use this input to trigger the Step Function daily:

```json
{
  "check_batches": [
    ["ec2_on_demand_standard_count", "elb_alb_count", "rds_instances"],
    ["iam_user_count", "vpc_count", "eip_count"],
    ["cloudwatch_alarm_count", "lambda_function_storage", "s3_bucket_count"],
    ["cloudformation_stack_count", "dynamodb_table_count", "ebs_snapshot_count"],
    ["rds_instance_snapshots", "route53_hosted_zone_count", "secretsmanager_secret_count"],
    ["ses_daily_sends"]
  ]
}
```

## 📬 Email Alerts
You’ll receive SNS alerts when usage exceeds 70%. Update thresholds as needed.

## 📌 Notes
- Make sure your Lambda IAM roles include access to SNS, AWS Quota, etc.
- Modify ARNs and Regions accordingly.