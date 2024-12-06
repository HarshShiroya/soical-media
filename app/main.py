from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # Import the CORSMiddleware
from app.routes import users, posts, feeds

app = FastAPI()

# Add CORS middleware to allow requests from any origin (use specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. In production, specify allowed domains.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods: GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

# Serve static files (HTML, JS, CSS) from the "static" folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Define custom routes to load the HTML files
@app.get("/")
async def get_home():
    return FileResponse("app/static/index.html")

@app.get("/register")
async def get_register():
    return FileResponse("app/static/register.html")

@app.get("/login")
async def get_login():
    return FileResponse("app/static/login.html")

@app.get("/feeds")
async def get_feed():
    return FileResponse("app/static/feed.html")

# Include your API routes
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(feeds.router, prefix="/feeds", tags=["feeds"])
