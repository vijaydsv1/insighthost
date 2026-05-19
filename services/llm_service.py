import os
import asyncio

from dotenv import load_dotenv

from google import generativeai as genai
from langchain_groq import ChatGroq


# =========================================================
# Load Environment Variables
# =========================================================
load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


# =========================================================
# Configure Gemini
# =========================================================
genai.configure(
    api_key=GEMINI_API_KEY
)


# =========================================================
# Gemini Model
# =========================================================
gemini_model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)


# =========================================================
# Groq Fallback Model
# =========================================================
groq_model = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.3
)


# =========================================================
# Generate LLM Response
# =========================================================
async def generate_llm_response(
    prompt: str
):

    """
    Main LLM Generation Service

    Responsibilities:
    - Gemini generation
    - Groq fallback
    - Retry handling
    - Future streaming support
    - Future model routing
    """

    # =====================================================
    # Try Gemini First
    # =====================================================
    try:

        response = gemini_model.generate_content(
            prompt
        )

        answer = response.text.strip()

        return {

            "answer": answer,

            "model": "gemini",

            "provider": "google"
        }

    except Exception as gemini_error:

        import traceback

        print("\n====== GEMINI ERROR ======")

        traceback.print_exc()

        print(str(gemini_error))

        print("==========================")

        print(
            "Switching to Groq fallback..."
        )

        # =================================================
        # Small Retry Delay
        # =================================================
        await asyncio.sleep(1)

    # =====================================================
    # Fallback to Groq
    # =====================================================
    try:

        groq_response = groq_model.invoke(
            prompt
        )

        answer = groq_response.content.strip()

        return {

            "answer": answer,

            "model": "llama-3.1-8b-instant",

            "provider": "groq"
        }

    except Exception as groq_error:

        import traceback

        print("\n====== GROQ ERROR ======")

        traceback.print_exc()

        print(str(groq_error))

        print("========================")

    # =====================================================
    # Final Failure Response
    # =====================================================
    return {

        "answer": (
            "Sorry, the assistant is currently "
            "unavailable. Please try again later."
        ),

        "model": "fallback_error",

        "provider": "none"
    }


# =========================================================
# Future Streaming Support
# =========================================================
async def stream_llm_response(
    text: str
):

    """
    Placeholder for future realtime token streaming

    Future:
    - Gemini streaming
    - Groq streaming
    - OpenAI streaming
    """

    words = text.split()

    for word in words:

        yield word + " "

        await asyncio.sleep(0.03)