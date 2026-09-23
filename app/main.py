import os

from dotenv import load_dotenv

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from api.chat_routes import (
    router as chat_router
)

from api.health_routes import (
    router as health_router
)

from api.websocket_routes import (
    router as websocket_router
)

from utils.constants import (
    APP_NAME,
    APP_VERSION
)

from api.camera_routes import router as camera_router

from api.video_routes import router as video_router


load_dotenv()


# =========================================================
# FastAPI Application
# =========================================================
app = FastAPI(

    title=APP_NAME,

    description=(
        "Realtime Multimodal AI "
        "Experience Center Assistant"
    ),

    version=APP_VERSION
)


# =========================================================
# CORS Configuration
# =========================================================
# Configurable per deployment: set CORS_ALLOWED_ORIGINS in .env
# to a comma-separated list of the actual frontend origin(s)
# this backend serves in production (e.g. the kiosk PC's real
# address). Falls back to local dev defaults.
CORS_ALLOWED_ORIGINS = [

    origin.strip()

    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

    if origin.strip()
]

app.add_middleware(

    CORSMiddleware,

    allow_origins=CORS_ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# Static Media Serving
# =========================================================
# Supports:
# - Images
# - Videos
# - PDFs
# - Assets
#
# Example:
# /media/images/demo.png
# /media/videos/demo.mp4
# /media/pdfs/brochure.pdf

app.mount(

    "/media",

    StaticFiles(directory="knowledge_base"),

    name="media"
)


# =========================================================
# API Routes
# =========================================================
app.include_router(

    chat_router,

    prefix="/api"
)

app.include_router(

    health_router,

    prefix="/api"
)

app.include_router(

    websocket_router,

    prefix="/api"
)

app.include_router(
    camera_router,
    prefix="/api"
)

app.include_router(
    video_router,
    prefix="/api"
)


# =========================================================
# Root Endpoint
# =========================================================

@app.get("/")
async def root():

    return {

        "success": True,

        "application": APP_NAME,

        "version": APP_VERSION,

        "status": "active",

        "message": (
            "InsightHost Backend Running"
        )
    }


# =========================================================
# Startup Event
# =========================================================
@app.on_event("startup")
async def startup_event():

    print("\n===================================")

    print(f"{APP_NAME} Started")

    print("Realtime AI Assistant Active")

    print(f"Version: {APP_VERSION}")

    print("===================================\n")


# =========================================================
# Shutdown Event
# =========================================================
@app.on_event("shutdown")
async def shutdown_event():

    print("\n===================================")

    print(f"{APP_NAME} Stopped")

    print("===================================\n")