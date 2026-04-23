from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.server import router as api_router
from api.voice_routes import router as voice_router

app = FastAPI(title="InsightHost AI Assistant")

# static files (audio responses)
app.mount("/static", StaticFiles(directory="."), name="static")

# include API routes
app.include_router(api_router)
app.include_router(voice_router)


@app.get("/")
def home():
    return {"message": "InsightHost AI Assistant API running"}