from app.auth_database import Base, engine
from app.models.auth_user import User
from app.routes.auth import router as auth_router
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.weapon import router as weapon_router
from app.routes.video import router as video_router
from app.routes.mobile import router as mobile_router
from app.routes.cameras import router as cameras_router
from app.routes.incidents import router as incidents_router


# Project paths
BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"
STUDENT_CROPS_FOLDER = BASE_DIR / "student_crops"

# Create folders if they do not exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
STUDENT_CROPS_FOLDER.mkdir(parents=True, exist_ok=True)


# FastAPI application
app = FastAPI(title="Autonomous AI Security Surveillance")

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/camera/start")
def start_camera():
    return {"status": "Camera Started"}


@app.get("/")
def home():
    return {
        "message": "Autonomous AI Security Surveillance Backend Running"
    }


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://bhakti200819.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes
app.include_router(router)

app.include_router(
    weapon_router,
    prefix="/weapon",
    tags=["Weapon Detection"],
)

app.include_router(video_router)

app.include_router(
    mobile_router,
    prefix="/mobile",
    tags=["Mobile Detection"],
)

app.include_router(
    cameras_router,
    prefix="/api",
    tags=["Camera Management"],
)

app.include_router(
    incidents_router,
    prefix="/api",
    tags=["Incidents"],
)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# Static Image Serving
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_FOLDER)),
    name="uploads",
)

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_FOLDER)),
    name="outputs",
)

app.mount(
    "/app/student_crops",
    StaticFiles(directory=str(STUDENT_CROPS_FOLDER)),
    name="student_crops",
)
