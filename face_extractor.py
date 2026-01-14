import argparse
import cv2
import os
from pathlib import Path

def extract_faces_from_directory(directory_path, output_dir):
    """
    Extracts faces from all images in the given directory using OpenCV's Haar Cascade.
    Saves each detected face as a separate image in the output directory.
    """
    # Load the pre-trained face detection cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # Process each image file in the directory
    for image_file in os.listdir(directory_path):
        if Path(image_file).suffix.lower() in image_extensions:
            image_path = os.path.join(directory_path, image_file)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not load image: {image_file}")
                continue
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
            
            print(f"Found {len(faces)} faces in {image_file}")
            
            for i, (x, y, w, h) in enumerate(faces):
                # Extract the face region
                face_roi = image[y:y+h, x:x+w]
                # Save the face with unique filename
                output_filename = f"{Path(image_file).stem}_face_{i}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                cv2.imwrite(output_path, face_roi)
                print(f"Saved face {i} to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract faces from images in a directory.")
    parser.add_argument("directory", help="Path to the directory containing images.")
    parser.add_argument("--output", "-o", default="extracted_faces", help="Output directory for faces (default: extracted_faces)")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
    else:
        extract_faces_from_directory(args.directory, args.output)
