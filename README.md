# 🖥️🎓 FaceReg - Hệ thống Quản lý Sinh viên qua Nhận diện Khuôn mặt

Hệ thống quản lý thông tin và điểm danh sinh viên sử dụng Công nghệ Nhận diện Khuôn mặt (Trí tuệ Nhân tạo). Ứng dụng Desktop chạy mượt mà, hoàn toàn không cần kết nối mạng để xử lý, mọi thứ được tính toán nội bộ tại máy tính của bạn thông qua sức mạnh từ module **YuNet & SFace (OpenCV ONNX)**.

## 📷 Demo Màn hình

### 1. Tab Điểm danh
> *Camera bắt khuôn mặt trực tiếp với tốc độ khung hình cao. Hiện tên và ô vuông nhận diện nhanh chóng thay vì sử dụng Dlib nặng nề.*

<div align="center">
  <img src="assets/attendance.png" alt="Màn hình Nhận diện điểm danh" width="600">
</div>

### 2. Tab Đăng ký Sinh viên
> *Đăng ký khuôn mặt bằng cách chụp tự động liên tiếp để trích xuất Feature Encodings.*

<div align="center">
  <img src="assets/registration.png" alt="Màn hình Đăng ký" width="600">
</div>

### 3. Tab Lịch sử Dữ liệu
> *Giao diện Treeview Tkinter lấy dữ liệu từ Backend CSV/Pickle theo chuẩn Data Science.*

<div align="center">
  <img src="assets/records.png" alt="Màn hình Data" width="600">
</div>

---

## ✨ Tính năng Nổi bật
- **⚡ 100% Thuần CPU / Gọn nhẹ**: Không yêu cầu card đồ họa (GPU). Sử dụng thuật toán YOLO thu nhỏ (`YuNet`) và trích xuất đặc trưng `SFace` đến từ OpenCV. Không dính lỗi cấu hình C++.
- **📸 Tự động Tăng cường Dữ liệu (Augmentation)**: Khi đăng ký, hệ thống kích hoạt thu ảnh liên tiếp và tự làm méo/sáng/lật ảnh để gia cố trí nhớ AI.
- **🔐 Quản lý Nội bộ an toàn**: Tất cả thông tin sinh viên được sao lưu chuẩn bảng tính (`*.csv`). Mã hóa khuôn mặt dạng vector 1x128 chiều ở file `.pkl`.

---

## 🚀 Hướng dẫn Cài đặt & Chạy ứng dụng

Bạn không cần code C++ hay cài công cụ Compiler (Visual Studio) để sử dụng phần mềm này! 

### Yêu cầu ban đầu
Máy của bạn cần phải cài đặt **Python 3.8 trở lên**. Khuyên dùng môi trường ảo (Virtual Environment).

### 1. Cài đặt thư viện
Clone repository này về máy và dùng quyền Terminal gõ:
```bash
pip install -r requirements.txt
```

### 2. Chạy Chương trình chính
Chỉ một nốt nhạc:
```bash
python main.py
```

---

## 📂 Kiến trúc Dự án
Dự án được phân cấp Folder để dễ bảo trì/nâng cấp:
```text
FaceReg/
├── core/
│   ├── data_manager.py     # Component kết nối Database CSV & Pickle
│   └── face_processor.py   # AI Component quản lý Face Extraction (SFace)
├── ui/
│   ├── app.py              # Xương sống của ứng dụng Tkinter
│   ├── attendance_tab.py   
│   ├── records_tab.py
│   └── registration_tab.py
├── data/                   # System sinh ra tự động khi bạn thao tác
│   ├── attendance.csv
│   ├── students.csv
│   └── faces/              # Các ma trận 1x128 chiều
├── models/
│   └── *.onnx              # Tệp tin bộ não AI (12MB)
├── assets/                 # Thư mục chứa ảnh phục vụ Github README
│   └── *.png
└── main.py                 # File thực thi chương trình
```

*Một sản phẩm để tối giản hóa quy trình điểm danh cực nhọc cho các Giảng viên/Giáo viên và tiết kiệm thời gian của Sinh Viên.* 🎈
