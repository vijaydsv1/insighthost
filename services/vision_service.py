import cv2


class VisionService:

    def __init__(self):

        self.camera = None

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

    def start_camera(self):

        self.camera = cv2.VideoCapture(0)

    def stop_camera(self):

        if self.camera:
            self.camera.release()

    def read_frame(self):

        if not self.camera:
            return None

        success, frame = self.camera.read()

        if not success:
            return None

        return frame

    def detect_person(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        return len(faces) > 0