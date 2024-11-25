from fastapi import FastAPI
from app.routes import users, posts, feeds

app = FastAPI()

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(feeds.router, prefix="/feeds", tags=["Feeds"])

@app.get("/")
def root():
    return {"message": "Welcome to the Social Media Platform API!"}
