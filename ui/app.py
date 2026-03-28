import tkinter as tk
from tkinter import ttk
from ui.registration_tab import RegistrationTab
from ui.attendance_tab import AttendanceTab
from ui.records_tab import RecordsTab

class FaceRegApp:
    def __init__(self, root, data_manager, face_processor):
        self.root = root
        self.root.title("Hệ thống Quản lý Sinh viên - Nhận diện Khuôn mặt")
        self.root.geometry("1000x700")
        
        self.data_manager = data_manager
        self.face_processor = face_processor
        
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11, 'bold'))
        
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Initialize Tabs
        self.registration_tab = RegistrationTab(self.notebook, self.face_processor)
        self.attendance_tab = AttendanceTab(self.notebook, self.face_processor, self.data_manager)
        self.records_tab = RecordsTab(self.notebook, self.data_manager)
        
        self.notebook.add(self.registration_tab, text='Đăng ký Khuôn mặt')
        self.notebook.add(self.attendance_tab, text='Điểm danh Camera')
        self.notebook.add(self.records_tab, text='Lịch sử & Dữ liệu')
        
        # On tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # Stop cameras in other tabs to release resource
        if tab_text == 'Đăng ký Khuôn mặt':
            self.attendance_tab.stop_camera()
            self.records_tab.refresh_data()
        elif tab_text == 'Điểm danh Camera':
            self.registration_tab.stop_camera()
            self.records_tab.refresh_data()
        elif tab_text == 'Lịch sử & Dữ liệu':
            self.registration_tab.stop_camera()
            self.attendance_tab.stop_camera()
            self.records_tab.refresh_data()

    def on_closing(self):
        self.registration_tab.stop_camera()
        self.attendance_tab.stop_camera()
        self.root.destroy()
