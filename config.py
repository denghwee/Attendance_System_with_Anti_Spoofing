CONFIG = {
    "detector": "mtcnn",   # "mtcnn", "retinaface", "dlib"
    "embedder": "facenet", # "facenet", "arcface", "dlib"
    "anti_spoof": "fasnet",
    "device": "cuda"
}

full_upload_dir = "temp_upload/full"
cut_upload_dir = "temp_upload/cut"
visitor_db_path = "visitor_db"
visitor_history_path = "visitor_history"
color_dark = (0, 0, 153)
color_white = (255, 255, 255)
file_db_config = 'visitors_db.csv'
file_history_config = 'visitors_history.csv'
user_color_config = '#000000'
title = "Face Recognition Attendance Sytem"
allowed_image_type = ['.png', 'jpg', '.jpeg']
attendance_db_path = "attendance.db"