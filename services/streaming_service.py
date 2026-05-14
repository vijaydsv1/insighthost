import asyncio


# =========================================================
# Simulated Streaming Generator
# =========================================================
async def stream_text_response(text: str):

    """
    Stream text word-by-word

    Future:
    - token streaming
    - realtime LLM chunks
    - streaming TTS
    """

    words = text.split()

    for word in words:

        yield word + " "

        await asyncio.sleep(0.03)