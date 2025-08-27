import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import auth, protected, chat

load_dotenv()

app = FastAPI(title="Backend with Roles & Access Control")

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change_me"),
    same_site="lax",
    https_only=False,
    max_age=60*60*24*7  # 7 days
)

# CORS setup
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(chat.router)