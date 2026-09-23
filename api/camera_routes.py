import base64

import cv2
import numpy as np

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from services.vision_service import VisionService

router = APIRouter(
    tags=["Camera"]
)

vision = VisionService()

# =========================================================
# NOTE: the backend intentionally does NOT open its own
# camera (cv2.VideoCapture) here. The frontend already holds
# the camera via the browser's getUserMedia() for the live
# preview, and most webcams only allow one exclusive
# consumer at a time - if the backend also tried to open it,
# whichever side grabbed the device first would starve the
# other. Detection instead runs on frames the frontend
# captures from its own video stream and posts to /detect.
# =========================================================


class CameraFrameRequest(BaseModel):

    # A base64-encoded JPEG/PNG frame, optionally as a full
    # "data:image/jpeg;base64,...." data URL.
    image: str


def _decode_frame(image_data: str):

    if "," in image_data:

        image_data = image_data.split(",", 1)[1]

    try:

        binary = base64.b64decode(image_data)

    except Exception:

        return None

    array = np.frombuffer(binary, dtype=np.uint8)

    return cv2.imdecode(array, cv2.IMREAD_COLOR)


def _detect_from_frame(image_data: str):

    frame = _decode_frame(image_data)

    if frame is None:

        return {
            "success": False,
            "person_detected": False,
            "face_count": 0,
            "dwell_seconds": 0.0,
            "message": "Unable to decode image"
        }

    # Anonymous presence detection only - no identity is
    # recognized or stored, just whether a face is visible,
    # how many, and for how long.
    status = vision.get_presence_status(frame)

    return {
        "success": True,
        **status,
        "message": (
            "Person detected"
            if status["person_detected"]
            else
            "No person detected"
        )
    }


@router.post("/camera/detect")
async def camera_detect(payload: CameraFrameRequest):

    if not payload.image:

        raise HTTPException(
            status_code=400,
            detail="No image data provided"
        )

    # Face detection is a blocking (OpenCV) call, so it runs
    # off the event loop to avoid stalling other requests
    # while the frontend polls this endpoint.
    return await run_in_threadpool(
        _detect_from_frame,
        payload.image
    )
