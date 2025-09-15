from typing import Optional
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
from dataclass import *
from PIL import Image
from models import *
import cv2
from utils import *

class FaceDetector:
    def __init__(self, image_size: int = 160, device: Optional[str] = None):
        self.models = FaceModels()
        self.device = self.models.device
        self.detector = self.models.detector

    def detect(self, frame_bgr: np.ndarray):
        """
        Returns (regions, crops, faces) for insightface,
        (regions, crops, None) for các detector khác.
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)

        regions: List[FaceRegion] = []
        crops: List[np.ndarray] = []

        # MTCNN
        if isinstance(self.detector, MTCNN):
            try:
                boxes, probs = self.detector.detect(frame_pil)
            except RuntimeError:
                img_tensor = torch.from_numpy(np.array(frame_pil)).float()
                img_tensor = img_tensor.permute(2, 0, 1)
                boxes, probs = self.detector.detect(img_tensor)

            if boxes is None:
                return regions, crops, None

            # Cắt tất cả khuôn mặt
            for box, p in zip(boxes, probs):
                if p is None:
                    continue
                x1, y1, x2, y2 = map(int, box)
                regions.append(FaceRegion((x1, y1, x2, y2), float(p)))

                middle = (x1 + x2) // 2
                cropped_img = crop_image_with_ratio(frame_rgb, 4, 3, middle)
                crops.append(cropped_img)

            return regions, crops, None

        # InsightFace (FaceAnalysis)
        from insightface.app.face_analysis import FaceAnalysis
        if isinstance(self.detector, FaceAnalysis):
            faces = self.detector.get(frame_rgb)
            h, w = frame_rgb.shape[:2]
            for face in faces:
                box = face.bbox.astype(int)
                x1, y1, x2, y2 = box
                # Clamp to image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                if x2 > x1 and y2 > y1:
                    score = float(face.det_score) if hasattr(face, "det_score") else 1.0
                    regions.append(FaceRegion((x1, y1, x2, y2), score))
                    face_rgb = frame_rgb[y1:y2, x1:x2]
                    crops.append(face_rgb)
            return regions, crops, faces  # Trả về luôn faces để dùng embedding

        # dlib
        import dlib
        if isinstance(self.detector, dlib.fhog_object_detector):
            dets = self.detector(frame_rgb)
            for det in dets:
                x1, y1, x2, y2 = det.left(), det.top(), det.right(), det.bottom()
                regions.append(FaceRegion((x1, y1, x2, y2), 1.0))
                face_rgb = frame_rgb[y1:y2, x1:x2]
                crops.append(face_rgb)
            return regions, crops, None

        raise ValueError("Unsupported detector type")

class FaceRecognizer:
    def __init__(self, device: Optional[str] = None):
        self.models = FaceModels()
        self.device = self.models.device
        self.embedder = self.models.embedder

    @torch.no_grad()
    def extract_embedding(self, register: bool = False, face_rgb: np.ndarray = None, detected_face=None) -> np.ndarray:
        # For facenet
        if isinstance(self.embedder, InceptionResnetV1):
            img = cv2.resize(face_rgb, (160, 160))
            img = img.astype(np.float32) / 255.0
            img = (img - 0.5) / 0.5
            tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(self.device)
            emb = self.embedder(tensor).cpu().numpy()[0]
            norm = np.linalg.norm(emb) + 1e-9
            return emb / norm

        # Nếu dùng insightface (arcface/retinaface) thì lấy embedding từ object face đã detect
        from insightface.app.face_analysis import FaceAnalysis
        if (isinstance(self.embedder, FaceAnalysis) and detected_face is not None):
            emb = detected_face.embedding
            norm = np.linalg.norm(emb) + 1e-9
            return emb / norm

        # For dlib
        import dlib
        if isinstance(self.embedder, dlib.face_recognition_model_v1):
            img = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR)
            dets = dlib.get_frontal_face_detector()(img, 1)
            if len(dets) == 0:
                return None
            shape = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")(img, dets[0])
            emb = self.embedder.compute_face_descriptor(img, shape)
            emb = np.array(emb)
            norm = np.linalg.norm(emb) + 1e-9
            return emb / norm

        raise ValueError("Unsupported embedder type")
    
    def recognize(self, probe_emb: np.ndarray, enrolled: list, threshold: float = 0.9):
        if probe_emb is None or not enrolled:
            return None
        best_staff, best_dist = None, float('inf')
        for s in enrolled:
            dist = np.linalg.norm(probe_emb - s.embedding)
            if dist < best_dist:
                best_dist = dist
                best_staff = s
        return best_staff if best_dist < threshold else None