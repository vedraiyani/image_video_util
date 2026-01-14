import argparse
import os
from PIL import Image
import sys
from pathlib import Path

def directory_path(path_str):
    """Custom type for argparse - validates directory exists."""
    if os.path.isdir(path_str):
        return os.path.abspath(path_str)
    else:
        raise argparse.ArgumentTypeError(f'"{path_str}" is not a valid directory')

def auto_rotate_image(input_path, output_dir):
    """Process single image with auto-rotation."""
    img = Image.open(input_path)
    
    # Check EXIF orientation
    if hasattr(img, '_getexif') and img._getexif():
        exif = img._getexif()
        orientation = exif.get(0x0112)
        
        if orientation == 3:  # 180°
            img = img.rotate(180, expand=True)
        elif orientation == 6:  # 90° CW
            img = img.rotate(270, expand=True)
        elif orientation == 8:  # 270° CW
            img = img.rotate(90, expand=True)
    
    # Generate output filename in specified directory
    base_name = Path(input_path).stem
    output_path = os.path.join(output_dir, f"{base_name}_rotated.jpg")
    
    img.save(output_path, quality=95)
    print(f"Processed: {input_path} -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Auto-rotate images from directory')
    parser.add_argument('directory', type=directory_path, 
                       help='Input directory containing images')
    parser.add_argument('-o', '--output', type=directory_path, 
                       help='Output directory (default: same as input)')
    
    args = parser.parse_args()
    
    # Use input dir as output if not specified
    output_dir = args.output or args.directory
    
    # Process all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    processed = 0
    
    for filename in os.listdir(args.directory):
        if Path(filename).suffix.lower() in image_extensions:
            input_path = os.path.join(args.directory, filename)
            auto_rotate_image(input_path, output_dir)
            processed += 1
    
    print(f"Processed {processed} images.")

if __name__ == "__main__":
    main()
