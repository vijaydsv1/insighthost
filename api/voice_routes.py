from fastapi import APIRouter

from speech.stt import listen
from speech.tts import speak
from pipeline.assistant_pipeline import run_assistant

router = APIRouter()


@router.get("/voice")
def voice():

    query = listen()

    if not query:
        return {
            "query": "",
            "answer": "Sorry, I could not hear you. Please try again.",
            "audio": ""
        }

    # run assistant pipeline
    answer = run_assistant(query)

    audio = speak(answer)

    return {
        "query": query,
        "answer": answer,
        "audio": f"/static/{audio}"
    }