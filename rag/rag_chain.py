from services.llm_service import generate_llm_response
from services.media_service import extract_media_assets

from vector_db.pinecone_client import vector_store


# =========================================================
# Main RAG Response Function
# =========================================================
async def get_rag_response(query: str):

    try:

        # =====================================================
        # Retrieve Relevant Documents
        # =====================================================
        docs = vector_store.similarity_search(
            query,
            k=4
        )

        # =====================================================
        # No Documents Found
        # =====================================================
        if not docs:

            return {

                "answer": (
                    "I could not find relevant information."
                ),

                "images": [],

                "videos": [],

                "pdfs": [],

                "links": [],

                "cards": [],

                "sources": [],

                "metadata": {}
            }

        # =====================================================
        # Build Context
        # =====================================================
        context_chunks = []

        for doc in docs:

            if doc.page_content:

                context_chunks.append(
                    doc.page_content
                )

        # =====================================================
        # Final Context
        # =====================================================
        context = "\n\n".join(
            context_chunks
        )

        # =====================================================
        # Extract Media Assets
        # =====================================================
        media_assets = extract_media_assets(
            docs
        )

        # =====================================================
        # Prompt
        # =====================================================
        prompt = f"""
You are InsightHost, a realtime AI Experience Center Assistant.

Answer the user's question ONLY using the provided context.

Guidelines:
- Be professional
- Be concise
- Be informative
- Do not hallucinate information
- If information is unavailable, clearly say so
- If relevant media exists, mention that supporting visuals,
  videos, PDFs, or links are available

Context:
{context}

Question:
{query}
"""

        # =====================================================
        # Generate LLM Response
        # =====================================================
        llm_response = await generate_llm_response(
            prompt
        )

        answer = llm_response.get(
            "answer",
            "No response generated."
        )

        model_used = llm_response.get(
            "model",
            "unknown"
        )

        # =====================================================
        # Final Structured Response
        # =====================================================
        return {

            "answer": answer,

            # =================================================
            # Media
            # =================================================
            "images": media_assets.get(
                "images",
                []
            ),

            "videos": media_assets.get(
                "videos",
                []
            ),

            "pdfs": media_assets.get(
                "pdfs",
                []
            ),

            "links": media_assets.get(
                "links",
                []
            ),

            # =================================================
            # Cards
            # =================================================
            "cards": media_assets.get(
                "cards",
                []
            ),

            # =================================================
            # Sources
            # =================================================
            "sources": media_assets.get(
                "sources",
                []
            ),

            # =================================================
            # Metadata
            # =================================================
            "metadata": {

                "model": model_used,

                "retrieved_docs": len(docs),

                "query": query
            }
        }

    except Exception as e:

        print(f"RAG Chain Error: {e}")

        return {

            "answer": (
                "Sorry, I encountered an error while "
                "processing your request."
            ),

            "images": [],

            "videos": [],

            "pdfs": [],

            "links": [],

            "cards": [],

            "sources": [],

            "metadata": {}
        }