import tkinter as tk
from ui.app import FaceRegApp
from core.data_manager import DataManager
from core.face_processor import FaceProcessor

def main():
    print("Khởi tạo hệ thống quản lý sinh viên...")
    
    # Init Backend Cores
    data_manager = DataManager(data_dir="data")
    face_processor = FaceProcessor(data_manager=data_manager)
    
    # Init Frontend Root
    root = tk.Tk()
    app = FaceRegApp(root, data_manager, face_processor)
    
    # Bind window close event to ensure cameras are closed properly
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("Mở giao diện UI...")
    # Start app Loop
    root.mainloop()

if __name__ == "__main__":
    main()
