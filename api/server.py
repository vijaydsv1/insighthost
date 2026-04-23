from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline.assistant_pipeline import run_assistant
from speech.tts import speak

router = APIRouter()


class Question(BaseModel):
    question: str


# -----------------------------
# Serve UI
# -----------------------------
@router.get("/ui")
def serve_ui():
    return FileResponse("ui/index.html")


# -----------------------------
# Wake assistant
# -----------------------------
@router.get("/wake")
def wake():

    message = "Hello, I am InsightHost. How can I help you?"

    audio = speak(message)

    return {
        "message": message,
        "audio": f"/static/{audio}"
    }


# -----------------------------
# Text Question
# -----------------------------
@router.post("/ask")
def ask(q: Question):

    if not q.question:
        return {
            "answer": "Please ask a question.",
            "audio": ""
        }

    # run assistant pipeline
    answer = run_assistant(q.question)

    audio = speak(answer)

    return {
        "answer": answer,
        "audio": f"/static/{audio}"
    }