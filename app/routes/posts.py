import os, json
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from typing import List
from app.routes.users import get_current_user
from app.models import User
import boto3
import pytz


# Load environment variables
load_dotenv()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["socialmedia"]
posts = db["posts"]

# FastAPI router
router = APIRouter()

# # SNS CLient
# sns_client = boto3.client('sns', region_name="AWS_REGION")  # Change region as needed
# sns_topic_arn = "SNS_TOPIC_ARN"  # Replace with your SNS topic ARN


class Notification(BaseModel):
    type: str 
    from_user: int  
    post_id: str 
    created_at: datetime 

def get_notifications_collection() -> Collection:
    return db["notifications"]


def send_notification_to_user(post_owner_id: int, post_id: str, action: str, from_user_id: int):
    """
    Adds a notification to the post owner's notifications array.
    """
    # Format the notification message
    notification = {
        "type": action,  # 'like' or 'comment'
        "from_user": from_user_id,  # The user performing the action
        "post_id": post_id,  # The post that was liked/commented on
        "created_at": datetime.utcnow().replace(tzinfo=pytz.UTC)
    }

    # Add the notification to the user's notifications array
    result = db.notifications.update_one(
        {"user_id": post_owner_id},  # Find the post owner by user_id
        {"$push": {"notifications": notification}}  # Push new notification to the array
    )

    if result.matched_count == 0:
        # If no document is found for this user_id, create a new one
        db.notifications.insert_one({
            "user_id": post_owner_id,
            "notifications": [notification]
        })

    print(f"Notification added to user {post_owner_id}'s notifications.")

# Define Models
class Post(BaseModel):
    user_id: int
    content: str
    media: List[str] = []
    likes: List[int] = []
    comments: List[dict] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string in JSON responses
        }


class Like(BaseModel):
    post_id: str


class Comment(BaseModel):
    post_id: str
    comment: str


# Helper function to validate ObjectId
def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")


# Dependency to get the MongoDB posts collection
def get_posts_collection() -> Collection:
    return db["posts"]


# Create a Post
@router.post("/createPost")
def create_post(post: Post, posts: Collection = Depends(get_posts_collection)):
    # Convert Pydantic model to dictionary and insert into MongoDB
    post_data = post.dict()
    result = posts.insert_one(post_data)
    return {"message": "Post created successfully!", "post_id": str(result.inserted_id)}


# Like a Post
@router.post("/like")
def like_post(
    like: Like,
    current_user: User = Depends(get_current_user),
    posts: Collection = Depends(get_posts_collection)
):

    post_id = validate_object_id(like.post_id)
    
    post = db.posts.find_one({"_id": post_id})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.id in post['likes']:
        # Remove the like if it already exists
        posts.update_one(
            {"_id": post_id},
            {"$pull": {"likes": current_user.id}}  # Pull the user id from the likes array
        )
        return {"message": "Like removed successfully."}
    else:
        # Add the like if it does not exist
        posts.update_one(
            {"_id": post_id},
            {"$addToSet": {"likes": current_user.id}}  # Add the user id to the likes array without duplicates
        )

    send_notification_to_user(post['user_id'], post_id, "liked", current_user.id)

    return {"message": "Post liked successfully"}


# Comment on a Post
@router.post("/comment")
def comment_on_post(
    comment: Comment,
    current_user: dict = Depends(get_current_user),
    posts: Collection = Depends(get_posts_collection)
):
    post_id = validate_object_id(comment.post_id)
    post = posts.find_one({"_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create the comment object
    new_comment = {
        "user_id": current_user.id,
        "comment": comment.comment,
        "timestamp": datetime.utcnow()
    }

    # Add the comment to the comments array
    posts.update_one(
        {"_id": post_id},
        {"$push": {"comments": new_comment}}
    )

    send_notification_to_user(post['user_id'], post_id, 'commented', current_user.id)
   
    return {"message": "Comment added successfully"}


# Get Notifications for the current user
@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    notifications_collection: Collection = Depends(get_notifications_collection),
):
    try:
        user_notifications = notifications_collection.find_one(
            {"user_id": current_user.id}
        )

        if user_notifications and "notifications" in user_notifications:
            return {"notifications": user_notifications["notifications"]}
        return {"notifications": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {e}")
