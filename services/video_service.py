import asyncio
import os
import time

from google import generativeai as genai

from services.llm_service import gemini_model


# =========================================================
# Video Understanding Service (Gemini native video input)
# =========================================================
# Used both for on-demand summarization / Q&A (via the API
# routes) and for building searchable video-summary documents
# at ingestion time (see rag/loader.py).

VIDEO_BASE_PATH = os.path.join(
    "knowledge_base",
    "videos"
)


def _resolve_video_path(filename: str) -> str:

    # os.path.basename strips any directory components so a
    # caller cannot request an arbitrary file elsewhere on disk.
    safe_name = os.path.basename(filename)

    path = os.path.join(VIDEO_BASE_PATH, safe_name)

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Video not found: {safe_name}"
        )

    return path


def _upload_and_wait(video_path: str, timeout_seconds: int = 120):

    uploaded_file = genai.upload_file(path=video_path)

    waited = 0

    while uploaded_file.state.name == "PROCESSING":

        if waited >= timeout_seconds:

            raise TimeoutError(
                f"Timed out waiting for Gemini to process "
                f"video: {video_path}"
            )

        time.sleep(2)

        waited += 2

        uploaded_file = genai.get_file(uploaded_file.name)

    if uploaded_file.state.name == "FAILED":

        raise RuntimeError(
            f"Gemini failed to process video: {video_path}"
        )

    return uploaded_file


# =========================================================
# Synchronous Core (safe to call from ingestion scripts)
# =========================================================
def summarize_video_sync(video_path: str) -> str:

    uploaded_file = _upload_and_wait(video_path)

    response = gemini_model.generate_content([

        uploaded_file,

        (
            "Summarize this video in 3-4 concise sentences for a "
            "corporate Experience Center visitor. Focus on what "
            "the video demonstrates, explains, or showcases."
        )
    ])

    return response.text.strip()


def answer_video_question_sync(video_path: str, question: str) -> str:

    uploaded_file = _upload_and_wait(video_path)

    response = gemini_model.generate_content([

        uploaded_file,

        (
            "Answer the following question using only what is "
            "shown or said in this video. If the video does not "
            "contain the answer, say so clearly.\n\n"
            f"Question: {question}"
        )
    ])

    return response.text.strip()


# =========================================================
# Async Wrappers (used by the API routes)
# =========================================================
async def summarize_video(filename: str) -> dict:

    try:

        video_path = _resolve_video_path(filename)

        summary = await asyncio.to_thread(
            summarize_video_sync,
            video_path
        )

        return {

            "success": True,

            "summary": summary
        }

    except FileNotFoundError as e:

        return {

            "success": False,

            "summary": "",

            "error": "not_found",

            "message": str(e)
        }

    except Exception as e:

        print(f"Video summarization error: {e}")

        return {

            "success": False,

            "summary": "",

            "error": "internal_error",

            "message": (
                "Sorry, I couldn't summarize this video right now."
            )
        }


async def answer_video_question(filename: str, question: str) -> dict:

    try:

        video_path = _resolve_video_path(filename)

        answer = await asyncio.to_thread(
            answer_video_question_sync,
            video_path,
            question
        )

        return {

            "success": True,

            "answer": answer
        }

    except FileNotFoundError as e:

        return {

            "success": False,

            "answer": "",

            "error": "not_found",

            "message": str(e)
        }

    except Exception as e:

        print(f"Video Q&A error: {e}")

        return {

            "success": False,

            "answer": "",

            "error": "internal_error",

            "message": (
                "Sorry, I couldn't process that video question "
                "right now."
            )
        }
