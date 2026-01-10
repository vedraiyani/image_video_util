import os
from PIL import Image
import argparse

def compress_image(input_path, output_path, quality=95):
    """
    Compress a single image using high JPEG quality to preserve visual quality.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save compressed image
        quality (int): JPEG quality (1-100, higher = better quality)
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (required for JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save with specified quality and optimization
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            print(f"Compressed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def compress_directory(input_dir, output_dir, quality=95):
    """
    Compress all images in input directory to output directory.
    
    Args:
        input_dir (str): Input directory containing images
        output_dir (str): Output directory for compressed images
        quality (int): JPEG quality (1-100)
    """
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    compressed_count = 0
    
    for filename in os.listdir(input_dir):
        if os.path.splitext(filename.lower())[1] in image_extensions:
            input_path = os.path.join(input_dir, filename)
            
            # Generate output filename (convert to .jpg)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_compressed.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            compress_image(input_path, output_path, quality)
            compressed_count += 1
    
    print(f"\nCompleted! Processed {compressed_count} images.")

def main():
    parser = argparse.ArgumentParser(description="Compress images without losing quality")
    parser.add_argument("input_dir", help="Input directory containing images")
    parser.add_argument("output_dir", help="Output directory for compressed images")
    parser.add_argument("-q", "--quality", type=int, default=95, 
                       help="JPEG quality (1-100, default: 95)")
    
    args = parser.parse_args()
    
    print(f"Compressing images from '{args.input_dir}' to '{args.output_dir}'")
    print(f"Quality setting: {args.quality}")
    
    compress_directory(args.input_dir, args.output_dir, args.quality)

if __name__ == "__main__":
    main()
