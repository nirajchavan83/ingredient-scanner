from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import classify_router, auth_router
from database import Base, engine
from models import user, scan  # 👈 ensures models are registered
import os

# ✅ Initialize FastAPI app
app = FastAPI(title="Ingredient Scanner API")

# ✅ Create all tables from SQLAlchemy models (users, scans, etc.)
Base.metadata.create_all(bind=engine)

# ✅ Setup CORS for all origins (you can restrict this for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Ensure upload folder exists
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

# ✅ Register your API routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(classify_router.router, prefix="/api")
