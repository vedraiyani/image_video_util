# compress_images
## Usage
Install Pillow first:

```bash
pip install Pillow
```

Command line usage:

```bash
python compress_images.py /path/to/input /path/to/output -q 95
```

Example:

```bash
python compress_images.py ./photos ./compressed_photos -q 92
```

### Key Features
- High-quality compression: Uses JPEG quality 95 (visually lossless)
​- Multi-format support: Handles PNG, JPEG, BMP, TIFF, WebP
​- Automatic RGB conversion: Handles RGBA/P modes for JPEG output
​- Progress feedback: Shows each processed file
- Safe output: Creates output directory automatically
- CLI interface: Easy directory-based batch processing

### Quality Settings
- 95-100: Visually lossless, minimal compression (~10-20% size reduction)
- 85-94: Near-lossless, good balance (~30-50% reduction)
- 75-84: Noticeable compression, still good quality (~50-70% reduction)
​
The script preserves original dimensions while reducing file size through efficient JPEG encoding with optimize=True.



# compress_videos

## Installation
```bash
# Install FFmpeg (required)
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg

# No Python packages needed!
```

## Usage Examples
```bash
# Basic compression (visually lossless)
python compress_videos.py ./videos ./compressed_videos

# Smaller files, still high quality
python compress_videos.py ./videos ./output -b 1M -r 1280x720 -c 25

# YouTube/Instagram quality
python compress_videos.py ./videos ./social -b 2500k -r 1080x1920 -c 23
```


## Quality Settings Guide

|CRF Value	|Quality Level	|Expected Size Reduction|
|-|-|-|
|18-20	|Visually lossless	|20-40% |
|21-23	|Excellent	|40-60%|
|24-26	|Very good	|60-75%|
|27-30	|Good	|75-85%|

## Key Features
- Preserves aspect ratio: Smart scaling without distortion
- Recursive processing: Handles subdirectories automatically
- H.264 + AAC: Universal compatibility (YouTube, mobile, web)
- Faststart: Web-optimized MP4 files
- Progress tracking: Real-time size comparison
- Error handling: Continues on individual file failures

Pro tip: CRF 23 + 2M bitrate typically reduces size 50-70% while maintaining excellent visual quality.
