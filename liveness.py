import cv2
import numpy as np
from typing import Optional
from test import test

class LivenessDetector:
    def __init__(self, device: Optional[str] = "0", active: bool = True):
        """
        Liveness detector with optional anti-spoofing model.
        If active=False, liveness check is bypassed.
        """
        self.active = active
        self.device = "0"


    def is_live(self, face_rgb: np.ndarray) -> bool:
        """
        Check if the given face is live or spoofed.
        Returns True for live faces, False for spoofed faces.
        """
        if not self.active:
            return True

        spoof = test(face_rgb, "./resources/anti_spoof_models", self.device)
        if spoof <= 1:
            return True
        else:
            return False