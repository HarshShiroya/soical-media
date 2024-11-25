from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_feed(user_id: int):
    # Fetch feed from the database
    return {"feed": "Feed for user"}
