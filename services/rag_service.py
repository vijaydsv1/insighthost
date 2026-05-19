import traceback
from rag.rag_chain import get_rag_response


# =========================================================
# Main RAG Service
# =========================================================
async def generate_rag_response(user_query: str):

    """
    Main RAG orchestration service

    Responsibilities:
    - Retrieve RAG response
    - Standardize multimodal output
    - Ensure frontend-ready response structure
    """

    try:

        # =====================================================
        # Get RAG Response
        # =====================================================
        response = await get_rag_response(user_query)

        # =====================================================
        # Standardized Structured Response
        # =====================================================
        return {

            "answer": response.get("answer", ""),

            "images": response.get("images", []),

            "videos": response.get("videos", []),

            "cards": response.get("cards", []),

            "sources": response.get("sources", []),

            "metadata": response.get("metadata", {}),

            "status": "success"
        }

    except Exception as e:

        print("\n========== RAG SERVICE ERROR ==========")

        traceback.print_exc()

        print("ERROR:", str(e))

        print("=======================================\n")

        raise e