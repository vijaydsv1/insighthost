from typing import List, Dict, Any, Optional

from pydantic import BaseModel


# =========================================================
# Media Card Model
# =========================================================
class MediaCard(BaseModel):

    title: str

    description: Optional[str] = ""

    image: Optional[str] = None

    video: Optional[str] = None

    source: Optional[str] = None


# =========================================================
# Assistant Response Model
# =========================================================
class AssistantResponse(BaseModel):

    success: bool = True

    status: str = "completed"

    answer: str

    images: List[str] = []

    videos: List[str] = []

    cards: List[MediaCard] = []

    sources: List[str] = []

    metadata: Dict[str, Any] = {}


# =========================================================
# Error Response Model
# =========================================================
class ErrorResponse(BaseModel):

    success: bool = False

    status: str = "error"

    message: str


# =========================================================
# WebSocket Event Model
# =========================================================
class WebSocketEvent(BaseModel):

    type: str

    payload: Dict[str, Any]