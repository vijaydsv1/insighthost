import threading
import time

import cv2


class VisionService:

    def __init__(self):

        self.camera = None

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        self._lock = threading.Lock()

        # Tracks how long someone has been continuously present.
        # No identity is stored - purely a timestamp.
        self._presence_since = None

    def start_camera(self):

        self.camera = cv2.VideoCapture(0)

    def stop_camera(self):

        if self.camera:
            self.camera.release()

    def read_frame(self):

        if not self.camera:
            return None

        with self._lock:

            success, frame = self.camera.read()

        if not success:
            return None

        return frame

    def detect_faces(self, frame):

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

        return faces

    def detect_person(self, frame):

        return len(self.detect_faces(frame)) > 0

    def get_presence_status(self, frame):

        """
        Anonymous presence detection: how many faces are visible
        and how long someone has been continuously present.

        Deliberately does not identify or store who is present -
        only that a face was detected and for how long.
        """

        faces = self.detect_faces(frame)

        face_count = len(faces)

        now = time.time()

        with self._lock:

            if face_count > 0:

                if self._presence_since is None:

                    self._presence_since = now

                dwell_seconds = round(
                    now - self._presence_since,
                    1
                )

            else:

                self._presence_since = None

                dwell_seconds = 0.0

        return {

            "person_detected": face_count > 0,

            "face_count": face_count,

            "dwell_seconds": dwell_seconds
        }
