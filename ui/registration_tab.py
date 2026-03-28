import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk

class RegistrationTab(ttk.Frame):
    def __init__(self, parent, face_processor):
        super().__init__(parent)
        self.face_processor = face_processor
        self.cap = None
        self.video_running = False
        self.capture_frames = []
        self.is_capturing = False
        self.capture_count = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Left Panel (Form & Controls)
        left_panel = ttk.Frame(self)
        left_panel.pack(side='left', fill='y', padx=20, pady=20)
        
        ttk.Label(left_panel, text="Thông tin Sinh viên", font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        ttk.Label(left_panel, text="Mã Số Sinh Viên (MSSV):").pack(anchor='w', pady=5)
        self.mssv_entry = ttk.Entry(left_panel, width=30)
        self.mssv_entry.pack(pady=5)
        
        ttk.Label(left_panel, text="Họ và Tên:").pack(anchor='w', pady=5)
        self.name_entry = ttk.Entry(left_panel, width=30)
        self.name_entry.pack(pady=5)
        
        self.btn_toggle_cam = ttk.Button(left_panel, text="Mở Camera", command=self.toggle_camera)
        self.btn_toggle_cam.pack(pady=20, fill='x')
        
        self.btn_register = ttk.Button(left_panel, text="Chụp ảnh & Đăng ký", command=self.start_capture, state='disabled')
        self.btn_register.pack(pady=5, fill='x')
        
        self.status_var = tk.StringVar()
        self.status_var.set("Trạng thái: Đang chờ...")
        ttk.Label(left_panel, textvariable=self.status_var, wraplength=200).pack(pady=20)

        # Right Panel (Video)
        right_panel = ttk.Frame(self)
        right_panel.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        self.video_label = ttk.Label(right_panel, text="Camera Off", background="black", foreground="white", anchor="center")
        self.video_label.pack(fill='both', expand=True)

    def toggle_camera(self):
        if not self.video_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Lỗi", "Không thể mở camera!")
                return
                
            self.video_running = True
            self.btn_toggle_cam.config(text="Đóng Camera")
            self.btn_register.config(state='normal')
            self.update_frame()
        else:
            self.stop_camera()
            
    def update_frame(self):
        if self.video_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_display = frame.copy()
                
                # Check if capturing data
                if self.is_capturing:
                    cv2.putText(frame_display, f"Capturing: {self.capture_count}/5", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.capture_frames.append(frame)
                    self.capture_count += 1
                    
                    if self.capture_count >= 5: # Take 5 frames
                        self.is_capturing = False
                        self.process_registration()
                        
                # Draw simple guide box
                h, w = frame_display.shape[:2]
                cv2.rectangle(frame_display, (w//4, h//6), (w*3//4, h*5//6), (0, 255, 0), 2)
                
                # Convert to PIL and TK
                rgb_frame = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                
                # Resize keeping aspect ratio
                max_w, max_h = 600, 480
                img.thumbnail((max_w, max_h))
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
            self.after(100, self.update_frame) # Update every 100ms
            
    def start_capture(self):
        mssv = self.mssv_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not mssv or not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập MSSV và Họ Tên!")
            return
            
        self.capture_frames = []
        self.capture_count = 0
        self.is_capturing = True
        self.status_var.set("Đang chụp ảnh, vui lòng nhìn vào camera...")
        self.btn_register.config(state='disabled')
        
    def process_registration(self):
        self.status_var.set("Đang xử lý mô hình...")
        self.update() # Force UI update
        
        mssv = self.mssv_entry.get().strip()
        name = self.name_entry.get().strip()
        
        # Use simple threading or run sync because it won't block for long (5 frames)
        success, msg = self.face_processor.register_new_face(mssv, name, self.capture_frames)
        
        if success:
            self.status_var.set("Thành công! Đã đăng ký.")
            messagebox.showinfo("Thành công", f"Đã đăng ký khuôn mặt cho {name} ({mssv})")
            self.mssv_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
        else:
            self.status_var.set("Thất bại. Chưa thấy rõ mặt.")
            messagebox.showerror("Thất bại", msg)
            
        self.btn_register.config(state='normal')
        
    def stop_camera(self):
        self.video_running = False
        if self.cap:
            self.cap.release()
        self.video_label.configure(image='', text="Camera Off")
        self.btn_toggle_cam.config(text="Mở Camera")
        self.btn_register.config(state='disabled')
