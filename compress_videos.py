import os
import subprocess
import argparse
from pathlib import Path

def compress_video(input_path, output_path, bitrate='2M', resolution='1920x1080', crf=23):
    """
    Compress a single video using FFmpeg with high quality settings.
    
    Args:
        input_path (str): Input video file
        output_path (str): Output compressed video file
        bitrate (str): Video bitrate (e.g., '2M' for 2Mbps)
        resolution (str): Output resolution (e.g., '1920x1080')
        crf (int): Constant Rate Factor (0-51, lower = better quality)
    """
    try:
        # FFmpeg command for high-quality compression
        command = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale={resolution}:force_original_aspect_ratio=decrease',  # Preserve aspect ratio
            '-c:v', 'libx264',  # H.264 codec
            '-crf', str(crf),   # Quality (18-23 is visually lossless)
            '-preset', 'medium', # Balance speed vs compression
            '-c:a', 'aac',      # Audio codec
            '-b:a', '128k',     # Audio bitrate
            '-movflags', '+faststart',  # Web optimization
            '-y',               # Overwrite output
            output_path
        ]
        
        subprocess.run(command, check=True, capture_output=True, text=True)
        input_size = os.path.getsize(input_path) / (1024*1024)  # MB
        output_size = os.path.getsize(output_path) / (1024*1024)  # MB
        print(f"✓ {os.path.basename(input_path)} ({input_size:.1f}MB → {output_size:.1f}MB)")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error compressing {input_path}: {e.stderr}")
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")

def compress_directory(input_dir, output_dir, bitrate='2M', resolution='1920x1080', crf=23):
    """
    Batch compress all videos from input directory to output directory.
    """
    # Supported video extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    compressed_count = 0
    
    for file_path in input_path.rglob('*'):
        if file_path.suffix.lower() in video_extensions:
            rel_path = file_path.relative_to(input_path)
            output_file = output_path / rel_path.with_suffix('.mp4')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Processing: {file_path.name}")
            compress_video(str(file_path), str(output_file), bitrate, resolution, crf)
            compressed_count += 1
    
    print(f"\n🎉 Completed! Processed {compressed_count} videos.")

def main():
    parser = argparse.ArgumentParser(description="Compress videos with high quality using FFmpeg")
    parser.add_argument("input_dir", help="Input directory containing videos")
    parser.add_argument("output_dir", help="Output directory for compressed videos")
    parser.add_argument("-b", "--bitrate", default='2M', help="Video bitrate (default: 2M)")
    parser.add_argument("-r", "--resolution", default='1920x1080', 
                       help="Output resolution (default: 1920x1080)")
    parser.add_argument("-c", "--crf", type=int, default=23, 
                       help="Quality (18-28, lower=better, default: 23)")
    
    args = parser.parse_args()
    
    print("🚀 High-Quality Video Compressor")
    print(f"Input:  {args.input_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Settings: {args.resolution} @ {args.bitrate} (CRF {args.crf})")
    print("-" * 60)
    
    compress_directory(args.input_dir, args.output_dir, args.bitrate, args.resolution, args.crf)

if __name__ == "__main__":
    main()
