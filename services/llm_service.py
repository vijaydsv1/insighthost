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
# Groq Model (Primary)
# =========================================================
# NOTE: Groq periodically retires/renames hosted models. If
# this ever starts failing with a 404 "model_not_found" error
# again, list what's currently available with:
#   from groq import Groq
#   Groq(api_key=...).models.list()
# and swap in an active general-purpose chat model's id.
groq_model = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b",
    temperature=0.3
)


# =========================================================
# Timeouts
# =========================================================
# Neither the Gemini nor the Groq SDK calls below are
# cancellable mid-flight, and neither has a built-in timeout.
# Without one, a single slow/hung network call would stall
# that request forever - in a voice kiosk, that looks exactly
# like "listening but never responding". asyncio.wait_for
# can't stop the underlying blocking call once started, but it
# does stop *waiting* on it, so the request fails over
# (Gemini -> Groq -> the final error message) instead of
# hanging indefinitely.
GEMINI_TIMEOUT_SECONDS = 20

GROQ_TIMEOUT_SECONDS = 15


# =========================================================
# Generate LLM Response
# =========================================================
async def generate_llm_response(
    prompt: str
):

    """
    Main LLM Generation Service

    Responsibilities:
    - Groq generation
    - Gemini fallback
    - Retry handling
    - Future streaming support
    - Future model routing
    """

    # =====================================================
    # Try Groq First
    # =====================================================
    # Groq is primary: Gemini's free-tier quota (5 requests/
    # minute) is too tight for a kiosk doing continuous
    # conversations (each turn also spends a Gemini call on
    # the relevance guardrail in rag_chain.py, plus video
    # summarize/Q&A draw from the same quota). Groq is used
    # first to keep normal chat responses off that quota
    # entirely, with Gemini kept only as a fallback.
    try:

        groq_response = await asyncio.wait_for(
            asyncio.to_thread(
                groq_model.invoke,
                prompt
            ),
            timeout=GROQ_TIMEOUT_SECONDS
        )

        answer = groq_response.content.strip()

        return {

            "answer": answer,

            "model": "openai/gpt-oss-20b",

            "provider": "groq"
        }

    except asyncio.TimeoutError:

        print(
            f"\nGroq timed out after "
            f"{GROQ_TIMEOUT_SECONDS}s, "
            f"switching to Gemini fallback..."
        )

    except Exception as groq_error:

        import traceback

        print("\n====== GROQ ERROR ======")

        traceback.print_exc()

        print(str(groq_error))

        print("========================")

        print(
            "Switching to Gemini fallback..."
        )

    # =====================================================
    # Fallback to Gemini
    # =====================================================
    try:

        # generate_content() is a blocking network call, so it
        # runs in a worker thread rather than on the event loop
        # (otherwise it would stall every other concurrent
        # request - chat, websocket, camera - for its duration).
        response = await asyncio.wait_for(
            asyncio.to_thread(
                gemini_model.generate_content,
                prompt
            ),
            timeout=GEMINI_TIMEOUT_SECONDS
        )

        answer = response.text.strip()

        return {

            "answer": answer,

            "model": "gemini",

            "provider": "google"
        }

    except asyncio.TimeoutError:

        print(
            f"\nGemini also timed out after "
            f"{GEMINI_TIMEOUT_SECONDS}s"
        )

    except Exception as gemini_error:

        import traceback

        print("\n====== GEMINI ERROR ======")

        traceback.print_exc()

        print(str(gemini_error))

        print("==========================")

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