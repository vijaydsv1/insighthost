from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.video_service import (
    summarize_video,
    answer_video_question
)


router = APIRouter(
    prefix="/video",
    tags=["Video"]
)


# =========================================================
# Request Models
# =========================================================
class VideoSummaryRequest(BaseModel):

    filename: str


class VideoQuestionRequest(BaseModel):

    filename: str

    question: str


# =========================================================
# Video Summarization
# =========================================================
@router.post("/summarize")
async def summarize(payload: VideoSummaryRequest):

    result = await summarize_video(payload.filename)

    if not result["success"]:

        status_code = (
            404
            if result.get("error") == "not_found"
            else 500
        )

        raise HTTPException(
            status_code=status_code,
            detail=result.get("message", "Failed to summarize video")
        )

    return {

        "success": True,

        "filename": payload.filename,

        "summary": result["summary"]
    }


# =========================================================
# Real-Time Video Q&A
# =========================================================
@router.post("/ask")
async def ask(payload: VideoQuestionRequest):

    if not payload.question or not payload.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    result = await answer_video_question(
        payload.filename,
        payload.question
    )

    if not result["success"]:

        status_code = (
            404
            if result.get("error") == "not_found"
            else 500
        )

        raise HTTPException(
            status_code=status_code,
            detail=result.get(
                "message",
                "Failed to process video question"
            )
        )

    return {

        "success": True,

        "filename": payload.filename,

        "question": payload.question,

        "answer": result["answer"]
    }
