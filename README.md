# Face Recognition Attendance System

Hệ thống điểm danh tự động sử dụng nhận diện khuôn mặt với khả năng chống giả mạo (anti-spoofing).

## 📋 Mô tả

Hệ thống điểm danh thông minh được xây dựng bằng Python và Streamlit, sử dụng công nghệ nhận diện khuôn mặt để tự động điểm danh nhân viên. Hệ thống hỗ trợ:

- **Nhận diện khuôn mặt tự động**: Sử dụng MTCNN và FaceNet để phát hiện và nhận diện khuôn mặt
- **Chống giả mạo (Anti-spoofing)**: Phát hiện ảnh giả, video hoặc mặt nạ để đảm bảo tính xác thực
- **Quản lý cơ sở dữ liệu**: Thêm, xóa và quản lý thông tin nhân viên
- **Lịch sử điểm danh**: Xem và xuất lịch sử điểm danh dưới dạng CSV
- **Giao diện web thân thiện**: Ứng dụng Streamlit với giao diện trực quan, dễ sử dụng

## 🖼️ Demo

### 1. Giao diện chính - Visitor Validation
![Demo 1](https://media.discordapp.net/attachments/1276917701717266526/1462674117995266251/image.png?ex=696f0cec&is=696dbb6c&hm=2a5b191ac0b6e8ab7d619949b1c350f3b1d9c6df59c182e993917a316fb82c7d&=&format=webp&quality=lossless&width=1552&height=873)
*Giao diện điểm danh với camera*

### 2. Xem lịch sử điểm danh
![Demo 2](https://media.discordapp.net/attachments/1276917701717266526/1462674243106902140/image.png?ex=696f0d0a&is=696dbb8a&hm=2c5dd8816082cac07da95284d77b794c603a6a06912d7819b1b8c29feb2b5d83&=&format=webp&quality=lossless&width=1552&height=873)
*Xem và xuất lịch sử điểm danh*

### 3. Đăng ký khuôn mặt mới
![Demo 3](https://media.discordapp.net/attachments/1276917701717266526/1462674872412016742/image.png?ex=696f0da0&is=696dbc20&hm=1496b407eefded7af286dcc30728818214cde4e9a6e92f2b559c2f11d1f75c8a&=&format=webp&quality=lossless&width=1547&height=873)
*Thêm nhân viên mới vào hệ thống*

### 4. Quản lý cơ sở dữ liệu
![Demo 4](https://media.discordapp.net/attachments/1276917701717266526/1462674899393839336/image.png?ex=696f0da7&is=696dbc27&hm=6e4f7cafb7e762d06d6eda9f11865f1cb8a27cdef8fa642b57d95712aa292682&=&format=webp&quality=lossless&width=1552&height=873)
*Xóa nhân viên khỏi hệ thống*

### 5. Tính năng Anti-Spoofing
![Demo 5](https://media.discordapp.net/attachments/1276917701717266526/1462675345584034028/image.png?ex=696f0e11&is=696dbc91&hm=89e7f58ae0bccd7ff3f3f36942e847ad0258868a6299ac7e052f528a8a6d02e4&=&format=webp&quality=lossless&width=1551&height=873)
*Hệ thống phát hiện và chặn các hình thức giả mạo (ảnh, video, mặt nạ)*

## 🚀 Tính năng

- ✅ **Điểm danh tự động**: Chỉ cần chụp ảnh để điểm danh
- ✅ **Nhận diện khuôn mặt chính xác**: Sử dụng FaceNet với độ chính xác cao
- ✅ **Chống giả mạo**: Phát hiện và chặn các hình thức tấn công bằng ảnh/video giả
- ✅ **Quản lý nhân viên**: Dễ dàng thêm/xóa nhân viên trong hệ thống
- ✅ **Lịch sử điểm danh**: Xem và xuất báo cáo điểm danh
- ✅ **Hỗ trợ nhiều phương thức đăng ký**: Camera hoặc upload ảnh
- ✅ **Giao diện web hiện đại**: Streamlit với UX/UI thân thiện

## 📦 Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- CUDA (nếu sử dụng GPU) - tùy chọn
- Webcam hoặc camera

### Các bước cài đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd AttendanceSystem
```

2. **Tạo môi trường ảo (khuyến nghị)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

4. **Tải các model cần thiết**

Các model anti-spoofing đã được bao gồm trong thư mục `resources/anti_spoof_models/`. Đảm bảo các file sau tồn tại:
- `2.7_80x80_MiniFASNetV2.pth`
- `4_0_0_80x80_MiniFASNetV1SE.pth`

Model detection đã có trong `resources/detection_model/`:
- `deploy.prototxt`
- `Widerface-RetinaFace.caffemodel`

## 🎯 Sử dụng

### Khởi động ứng dụng

```bash
streamlit run main.py
```

Ứng dụng sẽ tự động mở trong trình duyệt tại địa chỉ `http://localhost:8501`

### Hướng dẫn sử dụng

#### 1. Điểm danh (Visitor Validation)
- Chọn tab **"Visitor Validation"**
- Cho phép truy cập camera khi được yêu cầu
- Chụp ảnh khuôn mặt
- Hệ thống sẽ tự động nhận diện và điểm danh

#### 2. Xem lịch sử điểm danh (View Visitor History)
- Chọn tab **"View Visitor History"**
- Xem bảng lịch sử điểm danh
- Có thể xuất dữ liệu dưới dạng CSV
- Tìm kiếm ảnh theo ID điểm danh

#### 3. Đăng ký nhân viên mới (Add to Database)
- Chọn tab **"Add to Database"**
- Nhập tên nhân viên
- Chọn phương thức:
  - **Dùng Camera**: Chụp ảnh trực tiếp từ webcam
  - **Tải ảnh lên**: Upload ảnh từ máy tính
- Nhấn nút đăng ký

#### 4. Xóa nhân viên (Delete from Database)
- Chọn tab **"Delete from Database"**
- Chọn nhân viên cần xóa từ danh sách
- Nhấn nút "Xóa nhân viên"

## 🏗️ Cấu trúc dự án

```
AttendanceSystem/
├── main.py                 # File chính chạy Streamlit app
├── attendance.py           # Logic xử lý điểm danh
├── database.py             # Quản lý cơ sở dữ liệu SQLite
├── face_recognition.py     # Nhận diện và trích xuất embedding
├── camera.py               # Quản lý camera
├── liveness.py             # Phát hiện chống giả mạo
├── config.py               # Cấu hình hệ thống
├── models.py               # Load các model AI
├── dataclass.py            # Định nghĩa các data class
├── utils.py                # Các hàm tiện ích
├── requirements.txt        # Danh sách dependencies
├── attendance.db           # Database SQLite (tự động tạo)
├── resources/              # Thư mục chứa models
│   ├── anti_spoof_models/  # Models chống giả mạo
│   └── detection_model/    # Models phát hiện khuôn mặt
├── temp_upload/            # Thư mục tạm cho upload
│   ├── full/               # Ảnh đầy đủ
│   └── cut/                # Ảnh cắt khuôn mặt
├── visitor_db/             # Database visitor (CSV)
├── visitor_history/        # Lưu lịch sử ảnh điểm danh
└── demo/                   # Thư mục chứa ảnh demo
    └── images/
```

## ⚙️ Cấu hình

Có thể tùy chỉnh cấu hình trong file `config.py`:

```python
CONFIG = {
    "detector": "mtcnn",      # "mtcnn", "retinaface", "dlib"
    "embedder": "facenet",    # "facenet", "arcface", "dlib"
    "anti_spoof": "fasnet",
    "device": "cuda"          # "cuda" hoặc "cpu"
}
```

## 🔧 Công nghệ sử dụng

- **Streamlit**: Framework web application
- **PyTorch**: Deep learning framework
- **FaceNet (facenet-pytorch)**: Model nhận diện khuôn mặt
- **MTCNN**: Phát hiện khuôn mặt
- **OpenCV**: Xử lý ảnh và video
- **SQLite**: Cơ sở dữ liệu
- **Pandas**: Xử lý dữ liệu
- **PIL/Pillow**: Xử lý ảnh
- **InsightFace**: Face analysis (tùy chọn)

## 📝 Lưu ý

- Đảm bảo có đủ ánh sáng khi chụp ảnh để đạt độ chính xác cao
- Khuôn mặt cần rõ ràng, không bị che khuất
- Nếu sử dụng GPU, cài đặt `torch` với CUDA support
- Model anti-spoofing có thể cần thời gian xử lý, hãy kiên nhẫn

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Dự án này được phát hành dưới giấy phép MIT.

## 👨‍💻 Tác giả

Hệ thống được phát triển bởi DengHwee.

---

**Lưu ý**: Đây là hệ thống demo. Khi triển khai vào môi trường production, cần có các biện pháp bảo mật và tối ưu hóa phù hợp.
