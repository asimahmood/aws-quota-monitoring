import json
import logging
import boto3
import re
from aws_quota.cli import cli as quota_cli
from click.testing import CliRunner

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SNS_TOPIC_ARN = "arn:aws:sns:<Region>:<Account ID>:aws-quota-alerts"
sns = boto3.client("sns")

ALL_CHECKS = [
    "ec2_on_demand_standard_count", "elb_alb_count", "rds_instances", "iam_user_count",
    "vpc_count", "eip_count", "cloudwatch_alarm_count", "lambda_function_storage",
    "s3_bucket_count", "cloudformation_stack_count", "dynamodb_table_count",
    "ebs_snapshot_count", "rds_instance_snapshots", "route53_hosted_zone_count",
    "secretsmanager_secret_count", "ses_daily_sends"
]

def extract_usage(line):
    match = re.search(r": (\d+)/(\d+)", line)
    if match:
        used = int(match.group(1))
        limit = int(match.group(2))
        percent = round((used / limit) * 100, 2)
        status = "WARNING" if percent >= 70 else "OK"
        return {
            "used": used, "limit": limit, "percent_used": percent, "status": status
        }
    return { "used": None, "limit": None, "percent_used": None, "status": "ERROR" }

def lambda_handler(event, context):
    runner = CliRunner()
    results = {}
    alert_data = {}
    batch_size = 5
    for i in range(0, len(ALL_CHECKS), batch_size):
        batch = ALL_CHECKS[i:i + batch_size]
        for check in batch:
            result = runner.invoke(quota_cli, ["check", check])
            logger.info(f"[{check}] Output:\n{result.output}")
            usage_info = extract_usage(result.output)
            results[check] = usage_info
            if usage_info["percent_used"] and usage_info["percent_used"] >= 70:
                alert_data[check] = usage_info

    alert_needed = len(alert_data) > 0

    if alert_needed:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AWS Quota Alert",
            Message=json.dumps(alert_data, indent=2)
        )

    return {
        "results": results,
        "alert_data": alert_data,
        "alert_needed": alert_needed
    }