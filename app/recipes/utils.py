import os
import uuid

from flask import current_app
from PIL import Image, UnidentifiedImageError


def save_recipe_image(file_storage):
    """Save an uploaded recipe image under a random, collision-free filename.

    Returns the stored filename, or None if no file was provided.
    Raises ValueError if the file extension isn't in the allow-list, or if
    the file content doesn't actually decode as an image (extensions can be
    spoofed - e.g. a script renamed to ".png" - so we verify the real
    content with Pillow rather than trusting the filename alone).
    """
    if not file_storage or not file_storage.filename:
        return None

    original_name = file_storage.filename
    if "." not in original_name:
        raise ValueError("The uploaded file has no extension.")

    ext = original_name.rsplit(".", 1)[1].lower()
    allowed = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    if ext not in allowed:
        raise ValueError(f"Unsupported image type: .{ext}")

    # Verify the bytes are actually a decodable image before trusting them.
    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            img.verify()
    except (UnidentifiedImageError, OSError):
        raise ValueError("That file doesn't look like a valid image.")
    finally:
        file_storage.stream.seek(0)

    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, filename))
    return filename


def delete_recipe_image(filename):
    """Remove a previously stored recipe image, if it exists."""
    if not filename:
        return
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, filename)
    # Guard against path traversal - filename must resolve inside the upload folder.
    if os.path.commonpath([os.path.abspath(filepath), os.path.abspath(upload_folder)]) != os.path.abspath(upload_folder):
        return
    if os.path.exists(filepath):
        os.remove(filepath)
