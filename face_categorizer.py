import argparse
import cv2
import os
import re
import shutil
import numpy as np
from pathlib import Path
import face_recognition
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def extract_faces_from_directory(directory_path, output_dir):
    """Extract faces from images (same as before)"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    face_files = []
    
    for image_file in os.listdir(directory_path):
        if Path(image_file).suffix.lower() in image_extensions:
            image_path = os.path.join(directory_path, image_file)
            image = cv2.imread(image_path)
            if image is None:
                continue
                
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
            
            for i, (x, y, w, h) in enumerate(faces):
                face_roi = image[y:y+h, x:x+w]
                output_filename = f"{Path(image_file).stem}_face_{i}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                cv2.imwrite(output_path, face_roi)
                face_files.append(output_path)
    
    return face_files

def categorize_faces(face_dir, min_faces_per_category=2, eps=0.5):
    """Categorize faces using face embeddings and DBSCAN clustering"""
    face_files = list(Path(face_dir).glob("*.jpg")) + list(Path(face_dir).glob("*.png"))
    
    if len(face_files) < min_faces_per_category:
        print("Not enough faces for categorization")
        return
    
    # Extract face encodings
    encodings = []
    valid_faces = []
    
    print("Extracting face encodings...")
    for face_file in face_files:
        try:
            image = face_recognition.load_image_file(face_file)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                encodings.append(face_encodings[0])
                valid_faces.append(face_file)
        except:
            continue
    
    if len(encodings) < min_faces_per_category:
        print("Not enough valid faces with encodings")
        return
    
    encodings = np.array(encodings)
    
    # Cluster faces using DBSCAN
    print("Clustering faces...")
    clustering = DBSCAN(eps=eps, min_samples=min_faces_per_category, metric='euclidean').fit(encodings)
    labels = clustering.labels_
    
    # Create category directories
    Path("categories").mkdir(exist_ok=True)
    
    # Group faces by category
    n_categories = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"Found {n_categories} categories")
    
    for label in set(labels):
        if label == -1:  # Noise points
            continue
            
        category_dir = Path("categories") / f"category_{label}"
        category_dir.mkdir(exist_ok=True)
        
        category_faces = [f for i, f in enumerate(valid_faces) if labels[i] == label]
        print(f"Category {label}: {len(category_faces)} faces")
        
        for face_file in category_faces:
            output_path = category_dir / face_file.name
            cv2.imwrite(str(output_path), cv2.imread(str(face_file)))
    
    # Visualize categories (optional)
    visualize_categories(valid_faces, labels, n_categories)

def visualize_categories(face_files, labels, n_categories):
    """Create a visualization of categorized faces"""
    fig, axes = plt.subplots(2, max(3, n_categories//2), figsize=(15, 8))
    axes = axes.ravel()
    
    unique_labels = sorted(set(labels) - {-1})
    for i, label in enumerate(unique_labels[:len(axes)]):
        category_faces = [face_files[j] for j, l in enumerate(labels) if l == label]
        if category_faces:
            img = cv2.imread(str(category_faces[0]))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            axes[i].imshow(img)
            axes[i].set_title(f'Category {label}\n({len(category_faces)} faces)')
            axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('face_categories.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Visualization saved as 'face_categories.png'")


def copy_image_per_category(image_dir, category_dir, copy_dir):
    """ copy image per category """
    # Create category directories
    Path(copy_dir).mkdir(exist_ok=True)

    # list category path extract images
    category_imgs = list(Path(category_dir).glob("**/*.jpg")) + list(Path(category_dir).glob("**/*.png"))

    for category_img in category_imgs:
        img_segments = str(category_img).split('/') # category_dir/category/image
        
        # create category directory
        category_dir = Path(copy_dir) / img_segments[1]
        category_dir.mkdir(exist_ok=True)

        # prepare image name
        image_name = re.sub(r'_face_\d+', '', str(img_segments[2]))

        # copy image from source to category directory
        shutil.copy(Path(f"{image_dir}/{image_name}"), Path(f"{copy_dir}/{img_segments[1]}"))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and categorize faces from images.")
    parser.add_argument("directory", help="Path to directory containing images.")
    parser.add_argument("--output", "-o", default="extracted_faces", help="Output directory for faces")
    parser.add_argument("--categorize", "-c", action="store_true", help="Categorize extracted faces")
    parser.add_argument("--min-faces", type=int, default=2, help="Minimum faces per category")
    parser.add_argument("--similarity", type=float, default=0.5, help="Similarity threshold (0.3-0.7)")
    parser.add_argument("--copy-dir", "-d", default="copy", help="Output directory for categorized")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        exit(1)
    
    # Step 1: Extract faces
    # print("Step 1: Extracting faces...")
    # face_files = extract_faces_from_directory(args.directory, args.output)
    # print(f"Extracted {len(face_files)} faces to {args.output}")
    
    # Step 2: Categorize faces (if requested)
    # if args.categorize and face_files:
    #     print("\nStep 2: Categorizing faces...")
    #     categorize_faces(args.output, args.min_faces, args.similarity)

    # Step 3: Copy files into category
    # copy_image_per_category(args.directory, 'categories', args.copy_dir)

