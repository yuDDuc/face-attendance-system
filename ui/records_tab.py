import tkinter as tk
from tkinter import ttk

class RecordsTab(ttk.Frame):
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create a PanedWindow to show both tables side by side or vertically
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Upper Frame: Registered Students
        frame_students = ttk.LabelFrame(paned, text="Danh sách Sinh viên Đã Đăng ký")
        paned.add(frame_students, weight=1)
        
        # Lower Frame: Attendance Logs
        frame_attendance = ttk.LabelFrame(paned, text="Lịch sử Điểm danh")
        paned.add(frame_attendance, weight=1)
        
        # --- Students Table Setup ---
        cols_students = ('MSSV', 'Họ và Tên', 'Thời gian Đăng ký')
        self.tree_students = ttk.Treeview(frame_students, columns=cols_students, show='headings')
        for col in cols_students:
            self.tree_students.heading(col, text=col)
            self.tree_students.column(col, anchor="center")
            
        scrollbar_s = ttk.Scrollbar(frame_students, orient=tk.VERTICAL, command=self.tree_students.yview)
        self.tree_students.configure(yscroll=scrollbar_s.set)
        
        self.tree_students.pack(side=tk.LEFT, fill='both', expand=True, pady=5, padx=5)
        scrollbar_s.pack(side=tk.RIGHT, fill='y', pady=5)
        
        # --- Attendance Table Setup ---
        cols_att = ('MSSV', 'Họ và Tên', 'Thời gian Điểm danh')
        self.tree_attendance = ttk.Treeview(frame_attendance, columns=cols_att, show='headings')
        for col in cols_att:
            self.tree_attendance.heading(col, text=col)
            self.tree_attendance.column(col, anchor="center")
            
        scrollbar_a = ttk.Scrollbar(frame_attendance, orient=tk.VERTICAL, command=self.tree_attendance.yview)
        self.tree_attendance.configure(yscroll=scrollbar_a.set)
        
        self.tree_attendance.pack(side=tk.LEFT, fill='both', expand=True, pady=5, padx=5)
        scrollbar_a.pack(side=tk.RIGHT, fill='y', pady=5)
        
        # Refresh Button
        btn_refresh = ttk.Button(self, text="Làm mới Dữ liệu", command=self.refresh_data)
        btn_refresh.pack(pady=10)
        
        # Initial load
        self.refresh_data()

    def refresh_data(self):
        # Clear existing data
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)
        for row in self.tree_attendance.get_children():
            self.tree_attendance.delete(row)
            
        # Load Students Data
        df_students = self.data_manager.get_students()
        for idx, row in df_students.iterrows():
            # Convert NaN to empty string just in case
            mssv = str(row['mssv']) if pd.notnull(row['mssv']) else ""
            name = str(row['name']) if pd.notnull(row['name']) else ""
            reg_time = str(row['registered_at']) if pd.notnull(row['registered_at']) else ""
            self.tree_students.insert("", tk.END, values=(mssv, name, reg_time))
            
        # Load Attendance Data
        df_attendance = self.data_manager.get_attendance()
        # Sort by latest first
        if not df_attendance.empty and 'timestamp' in df_attendance.columns:
            df_attendance = df_attendance.sort_values(by='timestamp', ascending=False)
            
        for idx, row in df_attendance.iterrows():
            mssv = str(row['mssv']) if pd.notnull(row['mssv']) else ""
            name = str(row['name']) if pd.notnull(row['name']) else ""
            time = str(row['timestamp']) if pd.notnull(row['timestamp']) else ""
            self.tree_attendance.insert("", tk.END, values=(mssv, name, time))

import pandas as pd
