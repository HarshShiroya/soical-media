import os
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Load .env variables
load_dotenv()

router = APIRouter()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.social_app

class Post(BaseModel):
    user_id: int
    content: str

@router.post("/createPost")
def create_post(post: Post):
    db.posts.insert_one(post.dict())
    return {"message": "Post created successfully!"}


class Like(BaseModel):
    user_id: int
    post_id: str

class Comment(BaseModel):
    user_id: int
    post_id: str
    comment: str

@router.post("/like")
def like_post(like: Like):
    post = db.posts.find_one({"post_id": like.post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.posts.update_one({"post_id": like.post_id}, {"$addToSet": {"likes": like.user_id}})
    return {"message": "Post liked successfully"}

@router.post("/comment")
def comment_on_post(comment: Comment):
    post = db.posts.find_one({"post_id": comment.post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment = {"user_id": comment.user_id, "comment": comment.comment, "timestamp": datetime.utcnow()}
    db.posts.update_one({"post_id": comment.post_id}, {"$push": {"comments": new_comment}})
    return {"message": "Comment added successfully"}