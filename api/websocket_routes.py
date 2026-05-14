from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from pipeline.assistant_pipeline import run_assistant

from services.websocket_manager import manager
from services.streaming_service import (
    stream_text_response
)


router = APIRouter(
    tags=["WebSocket"]
)


# =========================================================
# WebSocket Endpoint
# =========================================================
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    # =====================================================
    # Connect Client
    # =====================================================
    await manager.connect(websocket)

    try:

        while True:

            # =================================================
            # Receive User Query
            # =================================================
            user_query = await websocket.receive_text()

            print(f"Received: {user_query}")

            # =================================================
            # Notify Stream Start
            # =================================================
            await manager.send_personal_message(

                {
                    "type": "stream_start"
                },

                websocket
            )

            # =================================================
            # Run Assistant Pipeline
            # =================================================
            response = await run_assistant(
                user_query
            )

            # =================================================
            # Extract Response Data
            # =================================================
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

            # =================================================
            # Stream Text Chunks
            # =================================================
            async for chunk in stream_text_response(
                answer
            ):

                await manager.send_personal_message(

                    {

                        "type": "stream_chunk",

                        "chunk": chunk
                    },

                    websocket
                )

            # =================================================
            # Final Structured Response
            # =================================================
            await manager.send_personal_message(

                {

                    "type": "assistant_response",

                    "success": True,

                    "answer": answer,

                    # =========================================
                    # Multimodal Assets
                    # =========================================
                    "images": images,

                    "videos": videos,

                    "pdfs": pdfs,

                    "links": links,

                    # =========================================
                    # Cards
                    # =========================================
                    "cards": cards,

                    # =========================================
                    # Sources
                    # =========================================
                    "sources": sources,

                    # =========================================
                    # Metadata
                    # =========================================
                    "metadata": metadata
                },

                websocket
            )

            # =================================================
            # Notify Stream End
            # =================================================
            await manager.send_personal_message(

                {
                    "type": "stream_end"
                },

                websocket
            )

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )

    except Exception as e:

        print(f"WebSocket Error: {e}")

        await manager.send_personal_message(

            {

                "type": "error",

                "message": (
                    "Failed to process websocket request"
                )
            },

            websocket
        )