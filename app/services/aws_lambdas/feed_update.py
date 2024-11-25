import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.social_app

def lambda_handler(event, context):
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    post_id = sns_message['post_id']
    user_id = sns_message['user_id']
    
    # Get followers of the user who created the post
    followers = db.followers.find({"followed_id": user_id})
    for follower in followers:
        db.feeds.insert_one({"user_id": follower['follower_id'], "post_id": post_id})
    return {"status": "Feed updated"}