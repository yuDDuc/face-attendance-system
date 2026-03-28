import os
import pandas as pd
import pickle
import datetime
from pathlib import Path

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.faces_dir = self.data_dir / "faces"
        self.students_csv = self.data_dir / "students.csv"
        self.attendance_csv = self.data_dir / "attendance.csv"
        
        # Init folders
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        
        # Init CSVs if not exists
        if not self.students_csv.exists():
            df = pd.DataFrame(columns=["mssv", "name", "registered_at"])
            df.to_csv(self.students_csv, index=False)
            
        if not self.attendance_csv.exists():
            df = pd.DataFrame(columns=["mssv", "name", "timestamp"])
            df.to_csv(self.attendance_csv, index=False)
            
    def save_student_encoding(self, mssv, name, encoding):
        # Save encoding to pickle
        file_path = self.faces_dir / f"{mssv}.pkl"
        with open(file_path, 'wb') as f:
            pickle.dump(encoding, f)
            
        # Append to students.csv
        df = pd.read_csv(self.students_csv)
        # Avoid duplicate, if exists update name and time
        if mssv in df['mssv'].values:
            df.loc[df['mssv'] == mssv, 'name'] = name
            df.loc[df['mssv'] == mssv, 'registered_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_row = {"mssv": mssv, "name": name, "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.students_csv, index=False)

    def load_all_encodings(self):
        known_encodings = []
        known_names = []
        known_mssvs = []
        
        if not self.faces_dir.exists():
            return known_encodings, known_names, known_mssvs
            
        try:
            df = pd.read_csv(self.students_csv)
            students_dict = {str(row['mssv']): str(row['name']) for _, row in df.iterrows()}
        except Exception:
            students_dict = {}

        for file_path in self.faces_dir.glob("*.pkl"):
            try:
                with open(file_path, 'rb') as f:
                    encoding = pickle.load(f)
                    mssv = file_path.stem
                    name = students_dict.get(mssv, "Unknown")
                    
                    known_encodings.append(encoding)
                    known_mssvs.append(mssv)
                    known_names.append(name)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        return known_encodings, known_names, known_mssvs
        
    def log_attendance(self, mssv, name):
        df = pd.read_csv(self.attendance_csv)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if already logged within last 5 minutes to avoid spam
        # This is a simple improvement for UX
        # Alternatively, just log every time requested
        new_row = {"mssv": mssv, "name": name, "timestamp": timestamp}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.attendance_csv, index=False)
        return timestamp

    def get_students(self):
        if self.students_csv.exists():
            return pd.read_csv(self.students_csv)
        return pd.DataFrame(columns=["mssv", "name", "registered_at"])
        
    def get_attendance(self):
        if self.attendance_csv.exists():
            return pd.read_csv(self.attendance_csv)
        return pd.DataFrame(columns=["mssv", "name", "timestamp"])
