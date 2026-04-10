from fastapi import APIRouter
from pydantic import BaseModel
from pipeline.assistant_pipeline import run_assistant

router = APIRouter()

class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QueryRequest):

    answer = run_assistant(request.question)

    return {
        "question": request.question,
        "answer": answer
    }