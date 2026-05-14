from fastapi import APIRouter
from fastapi import HTTPException

from pydantic import BaseModel

from pipeline.assistant_pipeline import (
    run_assistant
)

from utils.helpers import (
    clean_text,
    generate_session_id
)

from utils.constants import (
    STATUS_SUCCESS
)


router = APIRouter(

    prefix="/chat",

    tags=["Chat"]
)


# =========================================================
# Request Model
# =========================================================
class QuestionRequest(BaseModel):

    question: str

    session_id: str | None = None


# =========================================================
# Chat Endpoint
# =========================================================
@router.post("/ask")
async def ask_question(
    payload: QuestionRequest
):

    try:

        # =================================================
        # Clean Query
        # =================================================
        user_query = clean_text(
            payload.question
        )

        # =================================================
        # Validate Input
        # =================================================
        if not user_query:

            raise HTTPException(

                status_code=400,

                detail="Question cannot be empty"
            )

        # =================================================
        # Session ID
        # =================================================
        session_id = (

            payload.session_id

            or

            generate_session_id()
        )

        # =================================================
        # Run Assistant Pipeline
        # =================================================
        response = await run_assistant(

            user_query=user_query,

            session_id=session_id
        )

        # =================================================
        # Standardized Response
        # =================================================
        return {

            "success": True,

            "status": STATUS_SUCCESS,

            "session_id": session_id,

            "question": user_query,

            # =============================================
            # Main Response
            # =============================================
            "answer": response.get(
                "answer",
                ""
            ),

            # =============================================
            # Multimodal Assets
            # =============================================
            "images": response.get(
                "images",
                []
            ),

            "videos": response.get(
                "videos",
                []
            ),

            "pdfs": response.get(
                "pdfs",
                []
            ),

            "links": response.get(
                "links",
                []
            ),

            # =============================================
            # Cards
            # =============================================
            "cards": response.get(
                "cards",
                []
            ),

            # =============================================
            # Sources
            # =============================================
            "sources": response.get(
                "sources",
                []
            ),

            # =============================================
            # Metadata
            # =============================================
            "metadata": response.get(
                "metadata",
                {}
            )
        }

    except HTTPException as http_error:

        raise http_error

    except Exception as e:

        print(f"Chat Route Error: {e}")

        raise HTTPException(

            status_code=500,

            detail="Failed to process request"
        )