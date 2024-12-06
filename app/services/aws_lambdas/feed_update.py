from fastapi import APIRouter
from fastapi import  HTTPException, Depends
from pymongo import MongoClient
import os, json, datetime
from app.routes.users import get_current_user
from app.models import User
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["socialmedia"]
notifications_collection = mongo_db["notifications"]



def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    # Extract details from the event
    post_owner_id = event['post_owner_id']
    post_id = event['post_id']
    action = event['action']
    current_user_id = event['current_user_id']

    # Create notification message
    notification_message = create_notification_message(action)

    # Create the notification document to insert into MongoDB
    notification = {
        "user_id": post_owner_id,  # The user being notified (post owner)
        "action": notification_message,
        "post_id": post_id,
        "created_at": datetime.utcnow(),
        "read": False  # Initially set as unread
    }

    # Insert the notification into the MongoDB collection
    result = notifications_collection.insert_one(notification)
    print(f"Notification inserted with ID: {result.inserted_id}")

    return {
        'statusCode': 200,
        'body': json.dumps('Notification created successfully.')
    }

def create_notification_message(action):
    if action == "liked":
        return "liked your post"
    elif action == "commented":
        return "commented on your post"
    else:
        return "interacted with your post"
