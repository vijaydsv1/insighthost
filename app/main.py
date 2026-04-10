from fastapi import FastAPI
from api.voice_routes import router as voice_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "InsightHost AI Assistant API running"}

app.include_router(voice_router)