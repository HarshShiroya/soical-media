import os
import boto3
import json
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

sns_client = boto3.client(
    "sns",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

def publish_event(topic_arn, message):
    sns_client.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
    )
