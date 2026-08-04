import os
import glob
import uuid

from app.config import settings


def is_valid_file_format(extension: str) -> bool:
    valid_image_types = [".jpg", ".jpeg", ".png", ".heic", ".pdf", ".mov"]
    return extension.lower() in valid_image_types


def delete_file_from_dir(file_path: str):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"{file_path} does not exist.")
    except Exception as e:
        print(f"Error: {e}")
