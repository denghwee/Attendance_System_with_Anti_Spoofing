from collections import OrderedDict
import torch
from torch import nn
from facenet_pytorch import MTCNN, InceptionResnetV1
from insightface.app import FaceAnalysis
import dlib
import os
import cv2
import numpy as np
import argparse
import warnings
import time

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')

from config import CONFIG

class FaceModels:
    def __init__(self):
        self.device = torch.device(CONFIG['device'])
        self.detector_name = CONFIG["detector"]
        self.embedder_name = CONFIG["embedder"]

        self.detector = self._load_detector()
        self.embedder = self._load_embedder()

    def _load_detector(self):
        if self.detector_name == "mtcnn":
            return MTCNN(image_size=160, margin=0, min_face_size=20,
                        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
                        device=self.device, keep_all=True)
        elif self.detector_name == "retinaface":
            app = FaceAnalysis(name="buffalo_1")
            app.prepare(ctx_id=0 if str(self.device) == "cuda" else -1)
            return app
        elif self.detector_name == "dlib":
            return dlib.get_frontal_face_detector()
        else:
            raise ValueError(f"Unsupported detector: {self.detector_name}")

    def _load_embedder(self):
        if self.embedder_name == "facenet":
            return InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        elif self.embedder_name == "arcface":
            app = FaceAnalysis(name="buffalo_1")
            app.prepare(ctx_id=0 if str(self.device) == "cuda" else -1)
            return app
        elif self.embedder_name == "dlib":
            return dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
        else:
            raise ValueError(f"Unsupported embedder: {self.embedder_name}")
        
class AntiSpoofModel:
    def __init__(self, active: bool = True):
        self.device = torch.device(CONFIG['device'])
        self.active = active
        self.antispoof_name = CONFIG['anti_spoof']
        self.antispoof, self.image_cropper = self._load_antispoof()

    def _load_antispoof(self, device_id=0):
        if not self.active:
            return None, None
        if self.antispoof_name == "fasnet":
            model_test = AntiSpoofPredict(device_id)
            image_cropper = CropImage()
            return model_test, image_cropper
        return None, None

    def check_image(self, image):
        height, width, channel = image.shape
        if abs(width/height - 3/4) > 1e-3:  # tránh float precision
            print("Image is not appropriate! Height/Width should be 4/3.")
            return False
        return True

    def predict(self, image, model_dir, device_id=0):
        if self.antispoof is None or self.image_cropper is None:
            print("AntiSpoof model not initialized.")
            return None

        # Resize về 4:3
        image = cv2.resize(image, (int(image.shape[0] * 3 / 4), image.shape[0]))
        if not self.check_image(image):
            return None

        image_bbox = self.antispoof.get_bbox(image)
        prediction = np.zeros((1, 3))
        test_speed = 0

        # chạy từng model trong thư mục
        for model_name in os.listdir(model_dir):
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": image,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False

            img = self.image_cropper.crop(**param)
            start = time.time()
            prediction += self.antispoof.predict(img, os.path.join(model_dir, model_name))
            test_speed += time.time() - start

        label = np.argmax(prediction)
        confidence = prediction[0][label]  # giữ nguyên thay vì chia 2

        return label, confidence