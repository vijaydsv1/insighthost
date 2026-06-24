from fastapi import APIRouter

from services.vision_service import VisionService

router = APIRouter(
    tags=["Camera"]
)

vision = VisionService()

vision.start_camera()


@router.get("/camera/status")
async def camera_status():

    frame = vision.read_frame()

    if frame is None:

        return {
            "success": False,
            "person_detected": False,
            "message": "Unable to read camera"
        }

    detected = vision.detect_person(
        frame
    )

    return {
        "success": True,
        "person_detected": detected,
        "message": (
            "Person detected"
            if detected
            else
            "No person detected"
        )
    }