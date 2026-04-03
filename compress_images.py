import os
from PIL import Image

def compress_image(input_path, output_path, max_width=1280, quality=85):
    """Compress image by resizing and converting to JPEG"""
    try:
        img = Image.open(input_path)
        
        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPEG (much smaller than PNG)
        jpeg_path = output_path.replace('.png', '.jpg')
        img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
        
        original_size = os.path.getsize(input_path) / 1024
        new_size = os.path.getsize(jpeg_path) / 1024
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"{os.path.basename(input_path)}: {original_size:.1f} KB -> {new_size:.1f} KB ({reduction:.1f}% reduction)")
        return jpeg_path
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
        return None

if __name__ == "__main__":
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        print(f"Directory {screenshots_dir} not found!")
        exit(1)
    
    # Create backup directory
    backup_dir = os.path.join(screenshots_dir, "original")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print("Created backup directory")
    
    # Process all PNG files
    png_files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith('.png') and not f.startswith('original')]
    
    if not png_files:
        print("No PNG files found!")
        exit(1)
    
    print(f"Found {len(png_files)} PNG files. Compressing to JPEG...\n")
    
    for filename in png_files:
        input_path = os.path.join(screenshots_dir, filename)
        
        # Backup original if not already backed up
        backup_path = os.path.join(backup_dir, filename)
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(input_path, backup_path)
        
        # Compress to JPEG
        jpeg_path = compress_image(input_path, input_path, max_width=1280, quality=85)
    
    print("\nCompression complete! Images converted to JPEG format.")
    print("Original PNG files backed up in screenshots/original/")
    print("Note: Update LaTeX to use .jpg instead of .png")
