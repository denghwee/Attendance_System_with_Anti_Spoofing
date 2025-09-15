from datetime import datetime
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass

@dataclass
class FaceRegion:
    bbox: Tuple[int, int, int, int] # x1, y1, x2, y2
    prob: float


@dataclass
class Staff:
    id: int
    name: str
    embedding: np.ndarray # shape (512,)


@dataclass
class AttendanceLog:
    user_id: int
    timestamp: datetime
    status: str = "present"