import cv2
import numpy as np
from typing import Optional

class CameraManager:
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None


    def start(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")


    def capture(self) -> np.ndarray:
        if self.cap is None:
            raise RuntimeError("Camera not started")
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame")
        return frame


    def stop(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None