import os
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

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
