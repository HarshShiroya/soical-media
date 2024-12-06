from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import jwt
from jwt import PyJWTError

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic model to handle user registration
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


# Registration endpoint to create a new user
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Hash the password before saving to the database
    hashed_password = pwd_context.hash(user.password)
    
    # Create and save the user to the database
    db_user = User(username=user.username,email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get the user object with assigned ID
    
    return {"message": "User registered successfully!"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode({"user_id": db_user.id}, "your-secret-key", algorithm="HS256")
    return {"message": "Login successful!", "token": token}


from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "your-secret-key" 
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Query the user from the database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# Follow a user endpoint
@router.post("/follow/{user_id}")
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: int = 1):
    # Query the user to follow
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query the current user
    current_user_obj = db.query(User).filter(User.id == current_user).first()
    if user_to_follow in current_user_obj.followed:
        raise HTTPException(status_code=400, detail="You are already following this user")
    
    # Add the user to the current user's followed list (Many-to-Many relationship)
    current_user_obj.followed.append(user_to_follow)
    db.commit()
    
    return {"message": f"You are now following user {user_id}"}

# Unfollow a user endpoint
@router.post("/unfollow/{user_id}")
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: int = 1):
    # Query the user to unfollow
    user_to_unfollow = db.query(User).filter(User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query the current user
    current_user_obj = db.query(User).filter(User.id == current_user).first()
    if user_to_unfollow not in current_user_obj.followed:
        raise HTTPException(status_code=400, detail="You are not following this user")
    
    # Remove the user from the current user's followed list
    current_user_obj.followed.remove(user_to_unfollow)
    db.commit()
    
    return {"message": f"You unfollowed user {user_id}"}
