from services.vision_service import VisionService

vision = VisionService()

vision.start_camera()

frame = vision.read_frame()

print(
    "Person Detected:",
    vision.detect_person(frame)
)

vision.stop_camera()