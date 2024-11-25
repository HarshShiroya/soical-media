from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from passlib.context import CryptContext
from pydantic import BaseModel

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully!"}

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful!"}


@router.post("/follow/{user_id}")
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: int = 1):
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    current_user_obj = db.query(User).filter(User.id == current_user).first()
    current_user_obj.followed.append(user_to_follow)
    db.commit()
    return {"message": f"You are now following user {user_id}"}

@router.post("/unfollow/{user_id}")
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: int = 1):
    user_to_unfollow = db.query(User).filter(User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    current_user_obj = db.query(User).filter(User.id == current_user).first()
    current_user_obj.followed.remove(user_to_unfollow)
    db.commit()
    return {"message": f"You unfollowed user {user_id}"}