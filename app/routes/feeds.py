from fastapi import APIRouter
from fastapi import  HTTPException, Depends
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from app.routes.users import get_current_user
from app.models import User

router = APIRouter()
mongo_client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["socialmedia"]
posts_collection = mongo_db["posts"]

pg_connection = psycopg2.connect(
    dbname="socialmedia",
    user="postgres",
    password="qwerty",
    host="localhost",
    cursor_factory=RealDictCursor
)

@router.get("/")
def get_feed(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    # print(user_id.username, user_id.id)
    try:
        with pg_connection.cursor() as cursor:
            # Step 1: Fetch followed user IDs from PostgreSQL
            cursor.execute(
                """
                SELECT followed_id 
                FROM followers 
                WHERE follower_id = %s
                """,
                (user_id,)
            )
            followed_users = [row["followed_id"] for row in cursor.fetchall()]
            # print(followed_users)

        if not followed_users:
            return {"feed": [], "message": "You are not following anyone yet."}

        # Step 2: Fetch posts of followed users from MongoDB
        posts = posts_collection.find({"user_id": {"$in": followed_users}})
        feed = []

        for post in posts:
            post_data = {
                "post_id": str(post["_id"]),
                "user_id": post["user_id"],
                "content": post["content"],
                "media": post["media"][0],
                "likes": post.get("likes", []),
                "comments": post.get("comments", []),
            }
            feed.append(post_data)

        # Step 3: Return the feed in chronological order (sorted by timestamp)
        feed = sorted(feed, key=lambda x: x.get("created_at", ""), reverse=True)

        return {"feed": feed}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

