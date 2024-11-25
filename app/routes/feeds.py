from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_feed(current_user: int = 1):
    feed_posts = db.feeds.find({"user_id": current_user})
    posts = []
    for feed in feed_posts:
        post = db.posts.find_one({"post_id": feed["post_id"]})
        if post:
            posts.append(post)
    return {"feed": posts}

