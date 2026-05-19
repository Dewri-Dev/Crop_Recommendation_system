from PIL import Image
import os

def compress_image(file_path, target_size_kb=300):
    img = Image.open(file_path)
    quality = 95
    while quality > 10:
        img.save("temp_compressed.jpg", "JPEG", quality=quality, optimize=True)
        if os.path.getsize("temp_compressed.jpg") <= target_size_kb * 1024:
            break
        quality -= 5
    
    os.replace("temp_compressed.jpg", file_path)
    print(f"Compressed {file_path} to {os.path.getsize(file_path) / 1024:.2f} KB (quality={quality})")

if __name__ == "__main__":
    compress_image("images/ou_tenga.jpg")
