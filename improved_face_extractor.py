import argparse
import cv2
import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

def preprocess_image(image):
    """Preprocess image for better face detection"""
    # Convert to LAB color space and enhance contrast
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Denoise
    enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
    return enhanced

def is_likely_face(image_roi, min_area_ratio=0.7):
    """Filter false positives using simple heuristics"""
    gray_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    
    # Check aspect ratio (faces are roughly square)
    h, w = gray_roi.shape
    aspect_ratio = w / h
    if not 0.7 < aspect_ratio < 1.5:
        return False
    
    # Check for sufficient contrast (faces have skin texture)
    std_dev = np.std(gray_roi)
    if std_dev < 20:
        return False
    
    # Check for skin-like color distribution
    hsv_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)
    skin_mask = cv2.inRange(hsv_roi, np.array([0, 20, 70]), np.array([20, 255, 255]))
    skin_pixels = np.sum(skin_mask > 0)
    total_pixels = h * w
    skin_ratio = skin_pixels / total_pixels
    
    return skin_ratio > min_area_ratio

def extract_faces_improved(directory_path, output_dir):
    """Advanced face extraction with profile detection and false positive filtering"""
    
    # Load ALL available face cascades
    cascades = {
        'frontal': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
        'profile': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml'),
        'frontal_alt': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'),
        'frontal_alt2': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    }
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    face_files = []
    
    for image_file in os.listdir(directory_path):
        if Path(image_file).suffix.lower() in image_extensions:
            image_path = os.path.join(directory_path, image_file)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not load: {image_file}")
                continue
            
            print(f"Processing: {image_file}")
            
            # Preprocess image
            enhanced = preprocess_image(image)
            gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            
            all_faces = []
            
            # Detect with different cascades and parameters
            for name, cascade in cascades.items():
                if cascade.empty():
                    continue
                
                # Standard parameters
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, 
                                               minSize=(40, 40), maxSize=(500, 500))
                
                # Relaxed parameters for hard-to-detect faces
                faces_relaxed = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=2, 
                                                       minSize=(30, 30), maxSize=(500, 500))
                
                # Combine and deduplicate
                all_faces.extend(faces)
                all_faces.extend(faces_relaxed)
            
            # Remove duplicates (faces closer than 20% overlap)
            unique_faces = []
            for (x, y, w, h) in all_faces:
                is_duplicate = False
                for existing in unique_faces:
                    ex, ey, ew, eh = existing
                    if (abs(x - ex) < 0.2 * w and abs(y - ey) < 0.2 * h):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_faces.append((x, y, w, h))
            
            # Filter false positives and save valid faces
            valid_count = 0
            for i, (x, y, w, h) in enumerate(unique_faces):
                face_roi = image[y:y+h, x:x+w]
                
                # Apply false positive filter
                if is_likely_face(face_roi):
                    # Additional cleanup
                    face_roi = cv2.resize(face_roi, (160, 160))
                    face_roi = cv2.GaussianBlur(face_roi, (5, 5), 0)
                    
                    output_filename = f"{Path(image_file).stem}_face_{valid_count}.jpg"
                    output_path = os.path.join(output_dir, output_filename)
                    cv2.imwrite(output_path, face_roi)
                    face_files.append(output_path)
                    valid_count += 1
                    print(f"  Saved face {valid_count} ({w}x{h})")
                else:
                    print(f"  Rejected non-face region")
            
            print(f"Total valid faces from {image_file}: {valid_count}\n")
    
    return face_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Improved face extraction (front+profile)")
    parser.add_argument("directory", help="Path to directory containing images")
    parser.add_argument("--output", "-o", default="extracted_faces", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        exit(1)
    
    print("Using improved face detection (frontal + profile + false positive filtering)")
    face_files = extract_faces_improved(args.directory, args.output)
    print(f"\n✅ Extracted {len(face_files)} high-quality faces to '{args.output}'")
