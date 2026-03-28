import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk

class AttendanceTab(ttk.Frame):
    def __init__(self, parent, face_processor, data_manager):
        super().__init__(parent)
        self.face_processor = face_processor
        self.data_manager = data_manager
        self.cap = None
        self.video_running = False
        self.current_frame = None
        self.recognized_people = [] # List of tuples (name, mssv)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Panel (Controls)
        top_panel = ttk.Frame(self)
        top_panel.pack(side='top', fill='x', padx=20, pady=10)
        
        self.btn_toggle_cam = ttk.Button(top_panel, text="Mở Camera Nhận Diện", command=self.toggle_camera)
        self.btn_toggle_cam.pack(side='left', padx=5)
        
        self.btn_mark_attendance = ttk.Button(top_panel, text="Chốt Điểm Danh!", command=self.mark_attendance, state='disabled')
        self.btn_mark_attendance.pack(side='left', padx=5)
        
        self.label_count = ttk.Label(top_panel, text="Số người nhận diện: 0", font=('Helvetica', 12, 'bold'))
        self.label_count.pack(side='right', padx=20)

        # Main Panel (Video)
        self.video_label = ttk.Label(self, text="Camera Off", background="black", foreground="white", anchor="center")
        self.video_label.pack(fill='both', expand=True, padx=20, pady=10)

    def toggle_camera(self):
        if not self.video_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Lỗi", "Không thể mở camera!")
                return
                
            self.video_running = True
            self.btn_toggle_cam.config(text="Đóng Camera")
            self.btn_mark_attendance.config(state='normal')
            self.update_frame()
        else:
            self.stop_camera()
            
    def update_frame(self):
        if self.video_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Resize for faster recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                
                face_locations, face_names, face_mssvs = self.face_processor.detect_and_recognize(small_frame)
                
                # Clear tracking list for this frame
                self.recognized_people = []
                
                # Scale back face locations
                for (top, right, bottom, left), name, mssv in zip(face_locations, face_names, face_mssvs):
                    top *= 2
                    right *= 2
                    bottom *= 2
                    left *= 2
                    
                    if name != "Unknown":
                        self.recognized_people.append((name, mssv))

                    # Draw rect
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    
                    # Draw label
                    label = f"{name} ({mssv})" if name != "Unknown" else "Unknown"
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
                
                self.label_count.config(text=f"Số người nhận diện trúng: {len(self.recognized_people)}")
                
                # Display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                
                max_w, max_h = 800, 500
                img.thumbnail((max_w, max_h))
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
            # Use relatively fast update because it's real time.
            # Performance depends on CPU processing time needed by face_recognition.
            self.after(50, self.update_frame) 
            
    def mark_attendance(self):
        if not self.recognized_people:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy người quen trong khung hình!")
            return
            
        success_list = []
        for name, mssv in set(self.recognized_people): # unique people
            timestamp = self.data_manager.log_attendance(mssv, name)
            success_list.append(f"{name} ({mssv}) - {timestamp}")
            
        info = "\n".join(success_list)
        messagebox.showinfo("Thành công", f"Đã điểm danh cho:\n{info}")

    def stop_camera(self):
        self.video_running = False
        if self.cap:
            self.cap.release()
        self.video_label.configure(image='', text="Camera Off")
        self.btn_toggle_cam.config(text="Mở Camera Nhận Diện")
        self.btn_mark_attendance.config(state='disabled')
        self.label_count.config(text="Số người nhận diện: 0")
