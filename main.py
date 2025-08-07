from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import classify_router, auth_router
from database import Base, engine
from models import user, scan
import os

app = FastAPI(title="Ingredient Scanner API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

@app.get("/", tags=["Root"])
def root():
    return {"message": "Ingredient Scanner API is live 🎉"}

app.include_router(auth_router.router, prefix="/api")
app.include_router(classify_router.router, prefix="/api")
