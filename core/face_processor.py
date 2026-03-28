import cv2
import numpy as np
import os

class FaceProcessor:
    def __init__(self, data_manager, model_dir="models"):
        self.data_manager = data_manager
        
        # Load known faces from DataManager
        self.known_face_encodings, self.known_face_names, self.known_face_mssvs = self.data_manager.load_all_encodings()

        # Initialize detector and recognizer using OpenCV built-in ONNX models
        # This completely skips any dlib/C++ compiler requirements!
        detector_path = os.path.join(model_dir, "face_detection_yunet.onnx")
        recognizer_path = os.path.join(model_dir, "face_recognition_sface.onnx")
        
        self.detector = cv2.FaceDetectorYN.create(
            detector_path,
            "",
            (320, 320),
            score_threshold=0.8,
        )
        self.recognizer = cv2.FaceRecognizerSF.create(recognizer_path, "")

    def reload_known_faces(self):
        self.known_face_encodings, self.known_face_names, self.known_face_mssvs = self.data_manager.load_all_encodings()

    def _get_embedding(self, frame, face):
        # face is the output from YuNet (a 15-element array)
        aligned_face = self.recognizer.alignCrop(frame, face)
        feature = self.recognizer.feature(aligned_face)
        return feature

    def detect_and_recognize(self, frame, tolerance=1.128): 
        # SFace L2 distance threshold is commonly 1.128
        height, width, _ = frame.shape
        self.detector.setInputSize((width, height))
        
        _, faces = self.detector.detect(frame)
        
        face_locations = []
        face_names = []
        face_mssvs = []
        
        if faces is not None:
            for face in faces:
                x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
                # Ensure within frame bounds
                x = max(0, x)
                y = max(0, y)
                w = min(width - x, w)
                h = min(height - y, h)
                
                # Maintain the (top, right, bottom, left) convention from before
                face_locations.append((y, x+w, y+h, x)) 
                
                feature = self._get_embedding(frame, face)
                
                name = "Unknown"
                mssv = "Unknown"
                
                if len(self.known_face_encodings) > 0:
                    best_match_idx = -1
                    min_distance = float('inf')
                    
                    for i, known_feat in enumerate(self.known_face_encodings):
                        # Ensure shapes matched. The feature is 1x128 float32 matrix.
                        distance = self.recognizer.match(feature, known_feat, cv2.FaceRecognizerSF_FR_NORM_L2)
                        if distance < min_distance:
                            min_distance = distance
                            best_match_idx = i
                            
                    if min_distance <= tolerance: 
                        name = self.known_face_names[best_match_idx]
                        mssv = self.known_face_mssvs[best_match_idx]
                        
                face_names.append(name)
                face_mssvs.append(mssv)
                
        return face_locations, face_names, face_mssvs

    def register_new_face(self, mssv, name, frames):
        if not frames:
            return False, "No frames provided."
            
        all_features = []
        for frame in frames:
            height, width, _ = frame.shape
            self.detector.setInputSize((width, height))
            _, faces = self.detector.detect(frame)
            
            if faces is not None and len(faces) > 0:
                face = faces[0] # Take the most prominent face
                feature = self._get_embedding(frame, face)
                all_features.append(feature)
                
                # Simple augmentation: brightness
                for alpha in [0.8, 1.2]:
                    augmented = cv2.convertScaleAbs(frame, alpha=alpha, beta=0)
                    _, aug_faces = self.detector.detect(augmented)
                    if aug_faces is not None and len(aug_faces) > 0:
                        aug_feature = self._get_embedding(augmented, aug_faces[0])
                        all_features.append(aug_feature)
                        
                # Flip augmentation
                flipped = cv2.flip(frame, 1)
                _, flip_faces = self.detector.detect(flipped)
                if flip_faces is not None and len(flip_faces) > 0:
                    flip_feature = self._get_embedding(flipped, flip_faces[0])
                    all_features.append(flip_feature)

        if not all_features:
            return False, "Không tìm thấy mặt trong ảnh chụp."
            
        # Average feature for robust representation
        avg_feature = np.mean(all_features, axis=0)
        # Normalize the averaged embedding
        avg_feature = avg_feature / np.linalg.norm(avg_feature)
        
        self.data_manager.save_student_encoding(mssv, name, avg_feature)
        self.reload_known_faces()
        
        return True, "Thành công"
