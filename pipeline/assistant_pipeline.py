from services.rag_service import generate_rag_response

from services.memory_service import (
    add_message,
    get_conversation_history
)

from guardrails.input_validator import validate_input
from guardrails.intent_classifier import classify_intent
from guardrails.output_filter import filter_output
from guardrails.fallback_handler import fallback_response


# =========================================================
# Main Assistant Pipeline
# =========================================================
async def run_assistant(

    user_query: str,

    session_id: str = "default"
):

    try:

        # =====================================================
        # Input Validation
        # =====================================================
        if not validate_input(user_query):

            return fallback_response("invalid")

        # =====================================================
        # Intent Classification
        # =====================================================
        intent = classify_intent(user_query)

        print(f"Detected Intent: {intent}")

        # =====================================================
        # Restricted Queries
        # =====================================================
        if intent == "RESTRICTED":

            return fallback_response("restricted")

        # =====================================================
        # Out Of Scope Queries
        # =====================================================
        if intent == "OUT_OF_SCOPE":

            return fallback_response("out_of_scope")

        # =====================================================
        # Conversation History
        # =====================================================
        conversation_history = get_conversation_history(
            session_id
        )

        # =====================================================
        # Store User Message
        # =====================================================
        add_message(

            session_id=session_id,

            role="user",

            content=user_query
        )

        # =====================================================
        # Generate RAG Response
        # =====================================================
        response = await generate_rag_response(
            user_query
        )

        # =====================================================
        # Extract Response Fields
        # =====================================================
        answer = response.get(
            "answer",
            ""
        )

        images = response.get(
            "images",
            []
        )

        videos = response.get(
            "videos",
            []
        )

        pdfs = response.get(
            "pdfs",
            []
        )

        links = response.get(
            "links",
            []
        )

        cards = response.get(
            "cards",
            []
        )

        sources = response.get(
            "sources",
            []
        )

        metadata = response.get(
            "metadata",
            {}
        )

        # =====================================================
        # Output Filtering
        # =====================================================
        filtered_answer = filter_output(
            answer
        )

        # =====================================================
        # Store Assistant Response
        # =====================================================
        add_message(

            session_id=session_id,

            role="assistant",

            content=filtered_answer
        )

        # =====================================================
        # Final Structured Response
        # =====================================================
        return {

            "answer": filtered_answer,

            # =================================================
            # Multimodal Assets
            # =================================================
            "images": images,

            "videos": videos,

            "pdfs": pdfs,

            "links": links,

            # =================================================
            # Cards
            # =================================================
            "cards": cards,

            # =================================================
            # Sources
            # =================================================
            "sources": sources,

            # =================================================
            # Metadata
            # =================================================
            "metadata": {

                **metadata,

                "intent": intent,

                "session_id": session_id,

                "conversation_length": len(
                    conversation_history
                )
            },

            "status": "success"
        }

    except Exception as e:

        print(f"Assistant Pipeline Error: {e}")

        return fallback_response(
            "system_error"
        )