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
app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:3000",

        "http://127.0.0.1:3000"
    ],

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