import os
from PIL import Image

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

def is_image_file(fname: str) -> bool:
    return os.path.splitext(fname)[1].lower() in IMG_EXTS

def rename_files(directory, prefix):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and is_image_file(f)]
    files.sort()
    
    total_files = len(files)
    num_digits = len(str(total_files - 1)) if total_files > 0 else 1
    
    counter = 0
    for file in files:
        old_path = os.path.join(directory, file)
        try:
            img = Image.open(old_path)
            new_name = f"{prefix}_{counter:0{num_digits}d}.jpg"
            new_path = os.path.join(directory, new_name)
            img.convert('RGB').save(new_path, 'JPEG')
            os.remove(old_path)
            print(f"Renamed and converted {old_path} to {new_path}")
            counter += 1
        except Exception as e:
            print(f"Error processing {old_path}: {e}")

def main():
    base_path = "/home/ilmannafi/Documents/project-pbl/resize-citra"
    rename_files(os.path.join(base_path, "sakit"), "sakit")
    rename_files(os.path.join(base_path, "sehat"), "sehat")

if __name__ == "__main__":
    main()