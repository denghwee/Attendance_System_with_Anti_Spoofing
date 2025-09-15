from attendance import *
import argparse
import uuid ## random id generator
from streamlit_option_menu import option_menu
import streamlit as st
import os
import shutil
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from test import test
from utils import *
import torch
import datetime
from config import *

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FULL_SAVE_DIR = os.path.join(ROOT_DIR, full_upload_dir)
CUT_SAVE_DIR = os.path.join(ROOT_DIR, cut_upload_dir)
VISITOR_DB = os.path.join(ROOT_DIR, visitor_db_path)
VISITOR_HISTORY = os.path.join(ROOT_DIR, visitor_history_path)
COLOR_DARK  = color_dark
COLOR_WHITE = color_white
COLS_INFO   = ['Name']
COLS_ENCODE = [f'v{i}' for i in range(512)]
## Database
data_path       = VISITOR_DB
file_db         = file_db_config      ## To store user information
file_history    = file_history_config    ## To store visitor history information
db_path = attendance_db_path

################################################### Defining Static Data ###############################################

user_color      = user_color_config
title_webapp    = title

html_temp = f"""
            <div style="background-color:{user_color};padding:12px">
            <h1 style="color:white;text-align:center;font-size: 38px;">{title_webapp}</h1>
            </div>
            """
st.markdown(html_temp, unsafe_allow_html=True)

###################### Defining Static Paths ###################4
if st.sidebar.button('Click to Clear out all the data'):
    ## Clearing Visitor Database
    shutil.rmtree(VISITOR_DB, ignore_errors=True)
    os.mkdir(VISITOR_DB)
    ## Clearing Visitor History
    shutil.rmtree(VISITOR_HISTORY, ignore_errors=True)
    os.mkdir(VISITOR_HISTORY)

if not os.path.exists(VISITOR_DB):
    os.mkdir(VISITOR_DB)

if not os.path.exists(VISITOR_HISTORY):
    os.mkdir(VISITOR_HISTORY)
# st.write(VISITOR_HISTORY)

CONFIG["detector"] = "mtcnn"
CONFIG["embedder"] = "facenet"
CONFIG["device"] = "cuda"

pipeline = AttendancePipeline(db_path=db_path, camera_id=0)

def main():
    st.sidebar.header("About")
    st.sidebar.info("This webapp gives a demo of Attendance System"
                    " using 'Face Recognition', 'Anti-spoof'")
    
    selected_menu = option_menu(None,
        ['Visitor Validation', 'View Visitor History', 'Add to Database', 'Delete from Database'],
        icons=['camera', "clock-history", 'person-plus', 'trash'],
        ## icons from website: https://icons.getbootstrap.com/
        menu_icon="cast", default_index=0, orientation="horizontal")

    if selected_menu == "Visitor Validation":
        visitor_id = uuid.uuid1()
        img_file_buffer = st.camera_input("Take a picture")

        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()

            # convert image from opened file to np.array
            image_array = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            image_array_copy = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            # Nhận diện và check-in bằng pipeline
            attendance_id, user_id, timestamp = pipeline.get_check_in(image_array)

            attendance_id = str(attendance_id)
            safe_timestamp = (
                timestamp.strftime("%Y%m%d_%H%M%S")
                if hasattr(timestamp, "strftime")
                else str(timestamp).replace(":", "").replace("-", "").replace("T", "_")
            )

            filename = f"{attendance_id}_{user_id}_{safe_timestamp}.jpg"
            save_path = os.path.join(VISITOR_HISTORY, filename)

            os.makedirs(VISITOR_HISTORY, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(img_file_buffer.getbuffer())

    elif selected_menu == "View Visitor History":
        pipeline.view_history(visitor_history=VISITOR_HISTORY, db_path=db_path)

    elif selected_menu == "Add to Database":
        st.subheader("Đăng ký khuôn mặt mới")

        # Nhập tên người đăng ký
        name = st.text_input("Nhập tên của bạn")

        # Chọn phương thức đăng ký
        option = st.radio(
            "Chọn phương thức đăng ký",
            ["Dùng Camera", "Tải ảnh lên"]
        )

        if option == "Tải ảnh lên":
            uploaded_file = st.file_uploader("Tải ảnh khuôn mặt (jpg/png)", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None and name:
                # Lưu tạm file để đọc bằng OpenCV
                temp_path = os.path.join("temp_upload", uploaded_file.name)
                os.makedirs("temp_upload", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Nút đăng ký
                if st.button("Đăng ký từ ảnh"):
                    try:
                        user_id = pipeline.register_from_image(name, temp_path)
                        st.success(f"Đăng ký thành công: {name} (ID: {user_id})")
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        elif option == "Dùng Camera":
            camera_img = st.camera_input("Chụp ảnh khuôn mặt")
            if camera_img is not None and name:
                image = Image.open(camera_img).convert("RGB")

                if st.button("Đăng ký từ Camera"):
                    try:
                        img_np = np.array(image)
                        regions, crops, faces = pipeline.detector.detect(img_np)
                        if not crops:
                            st.error("Không phát hiện khuôn mặt.")
                        else:
                            areas = [c.shape[0] * c.shape[1] for c in crops]
                            idx = int(np.argmax(areas))
                            face_rgb = crops[idx]
                            detected_face = faces[idx] if faces is not None else None

                            if detected_face is not None:
                                emb = pipeline.recognizer.extract_embedding(detected_face=detected_face)
                            else:
                                emb = pipeline.recognizer.extract_embedding(face_rgb=face_rgb)

                            if emb is not None:
                                user_id = pipeline.db.insert_staff(name=name, embedding=emb)

                                full_img_path = os.path.join(FULL_SAVE_DIR, f"{user_id}_{name}_full.jpg")
                                image.save(full_img_path)

                                face_img_path = os.path.join(CUT_SAVE_DIR, f"{user_id}_{name}_face.jpg")
                                Image.fromarray(face_rgb).save(face_img_path)

                                st.success(f"Đăng ký thành công: {name} (ID: {user_id})")
                            else:
                                st.error("Không thể trích xuất embedding.")
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    elif selected_menu == "Delete from Database":
        st.subheader("Xóa nhân viên khỏi hệ thống")

        staff_list = pipeline.db.get_all_staffs()
        if not staff_list:
            st.info("Hiện chưa có nhân viên nào trong cơ sở dữ liệu.")
        else:
            df_staff = pd.DataFrame([{"ID": s.id, "Name": s.name} for s in staff_list])
            st.dataframe(df_staff, use_container_width=True)

            staff_names = [f"{s.id} - {s.name}" for s in staff_list]
            selected_staff = st.selectbox("Chọn nhân viên để xóa", staff_names)

            if st.button("Xóa nhân viên"):
                staff_id = int(selected_staff.split(" - ")[0])

                try:
                    pipeline.db.delete_staff(staff_id)
                    st.success(f"Đã xóa nhân viên ID: {staff_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi xóa: {e}")

if __name__ == "__main__":
    main()