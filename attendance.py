from database import *
from camera import *
from face_recognition import *
from liveness import *
from PIL import Image
from config import *
import pandas as pd
import os
import streamlit as st

class AttendanceManager:
    def __init__(self, db: DatabaseHandler):
        self.db = db

    def check_in(self, user_id, anti_spoof_status, status="present"):
        timestamp = datetime.now().isoformat()
        return self.db.insert_attendance(user_id=user_id, status=status, timestamp=timestamp, anti_spoof_status=anti_spoof_status)
    
    def get_logs(self, date: Optional[str] = None) -> List[AttendanceLog]:
        if date is None:
            date = datetime().now().date().isoformat()
            return self.db.get_attendance_by_date(date)
        
class AttendancePipeline:
    def __init__(self, db_path: str = "attendance.db", camera_id: int = 0):
        self.db = DatabaseHandler(db_path=db_path)
        self.camera = CameraManager(camera_id=camera_id)
        self.detector = FaceDetector()
        self.liveness = LivenessDetector(active=True)
        self.recognizer = FaceRecognizer()
        self.attendance = AttendanceManager(self.db)
    
    def register_from_image(self, name: str, image_path: str) -> int:
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)
        bgr = cv2.imread(image_path)
        if bgr is None:
            raise RuntimeError(f"Cannot read image: {image_path}")
        regions, crops, faces = self.detector.detect(bgr)
        if not crops:
            raise RuntimeError(f"No face detected in registration image")
        # Pick the largest face
        areas = [c.shape[0] * c.shape[1] for c in crops]
        idx = int(np.argmax(areas))
        face_rgb = crops[idx]
        detected_face = faces[idx] if faces is not None else None
        if detected_face is not None:
            emb = self.recognizer.extract_embedding(detected_face=detected_face)
        else:
            emb = self.recognizer.extract_embedding(face_rgb=face_rgb)
        if emb is None:
            raise ValueError("No face or embedding found in the provided image. Please use a clear image with a visible face.")
        return self.db.insert_staff(name=name, embedding=emb)
    
    def register_from_camera(self, name: str, save_path: str = None) -> int:
        print("Press \"Space\" to begin registration or press \"Q\" to cancel registration.")
        self.camera.start()
        try:
            while True:
                frame = self.camera.capture()
                if frame is None:
                    print("Failed to capture frame from camera.")
                    continue

                display_frame = frame.copy()
                cv2.imshow("Register - Press \"Space\", Cancel - Press \"Q\"", display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("Registration cancelled.")
                    cv2.destroyAllWindows()
                    return None

                if key == 32:  # Phím Space
                    regions, crops, faces = self.detector.detect(frame)
                    if crops:
                        face_crop = crops[0]
                        detected_face = faces[0] if faces is not None else None
                        if detected_face is not None:
                            emb = self.recognizer.extract_embedding(detected_face=detected_face)
                        else:
                            emb = self.recognizer.extract_embedding(face_rgb=face_crop)
                        if emb is not None:
                            if save_path:
                                cv2.imwrite(save_path, frame)
                            # Kiểm tra tên đã tồn tại chưa
                            if self.db.get_staff_by_name(name) is not None:
                                print(f"Name '{name}' existed. Please choose another name.")
                                continue
                            user_id = self.db.insert_staff(name=name, embedding=emb)
                            print(f"Registration success with {name} (ID: {user_id})")
                            cv2.destroyAllWindows()
                            return user_id
                        else:
                            print("Face detected but can't embedding. Try again!")
                    else:
                        print("Face didn't detected. Try again.")

        finally:
            self.camera.stop()
            cv2.destroyAllWindows()
        return None

    def delete_from_db(self, staff_id: int) -> int:
        return self.db.delete_staff(staff_id=staff_id)

    def _draw_regions(self, frame_bgr: np.ndarray, regions: List[FaceRegion], names: List[str]):
        for region, name in zip(regions, names):
            x1, y1, x2, y2 = region.bbox
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (10, 255, 0), 2)
            cv2.putText(frame_bgr, name, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    def get_check_in(self, frame):
        if frame is not None:
            regions, crops, faces = self.detector.detect(frame)

            if not crops:
                st.warning("No face detected, please try again.")
                return None, None, None

            # chọn mặt lớn nhất
            areas = [c.shape[0] * c.shape[1] for c in crops]
            idx = int(np.argmax(areas))
            face_rgb = crops[idx]
            detected_face = faces[idx] if faces is not None else None

            anti_spoof_status = self.liveness.is_live(face_rgb)

            # if not anti_spoof_status:
            #     st.error("Spoofing suspected — check-in blocked.")
            #     return

            if detected_face is not None:
                probe = self.recognizer.extract_embedding(detected_face=detected_face)
            else:
                probe = self.recognizer.extract_embedding(face_rgb=face_rgb)

            staffs = self.db.get_all_staffs()
            matched = self.recognizer.recognize(probe, staffs)

            if matched is None:
                st.error("Unknown face — not checked in.")
                return None, None, None
            else:
                attendance_id, user_id, attendance_timestamp = self.attendance.check_in(user_id=matched.id, anti_spoof_status=anti_spoof_status)
                st.success(f"{matched.name} checked in at {datetime.now().strftime('%H:%M:%S')}")

                self._draw_regions(frame, [regions[idx]], [matched.name])
                st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                        caption="Attendance Result", width='content')
                
                return attendance_id, user_id, attendance_timestamp
                
    def view_history(self, visitor_history, db_path):
        df_attendance = self.db.get_all_attendance()

        if df_attendance.empty:
            st.info("📭 Không có dữ liệu điểm danh.")
            return None

        st.subheader("📋 Lịch sử điểm danh")
        st.dataframe(df_attendance)

        csv_data = df_attendance.to_csv(index=False)
        st.download_button(
            label="💾 Xuất CSV",
            data=csv_data,
            file_name="attendance_history.csv",
            mime="text/csv"
        )

        selected_id = st.selectbox(
            "🔍 Tìm ảnh theo ID (attendance.id)",
            options=['None'] + list(df_attendance['id'].astype(str))
        )

        if selected_id != 'None':
            avail_files = [
                f for f in os.listdir(visitor_history)
                if f.lower().endswith(tuple(allowed_image_type))
                and (f.startswith(f"{selected_id}_") or f.startswith(f"{selected_id}."))  # hỗ trợ cả dấu chấm
            ]

            if avail_files:
                newest_file = max(
                    avail_files,
                    key=lambda f: os.path.getmtime(os.path.join(visitor_history, f))
                )
                img_path = os.path.join(visitor_history, newest_file)
                st.image(Image.open(img_path), caption=f"Ảnh mới nhất của ID {selected_id}")
            else:
                st.warning("Không tìm thấy ảnh tương ứng.")


        return df_attendance