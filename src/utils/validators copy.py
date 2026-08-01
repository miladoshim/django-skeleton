from django.forms import ValidationError
from persian_tools import national_id, phone_number
from persian_tools.bank import card_number, sheba


def validate_shaba(value):
    if not sheba.validate(value):
        raise ValidationError("شماره شبا نامعتبر است")


def validate_card_number(value):
    if not card_number.validate(value):
        raise ValidationError("شماره کارت نامعتبر است")


def validate_national_id(value):
    if not national_id.validate(value):
        raise ValidationError("شماره ملی نامعتبر است")


def validate_phone_number(value):
    if not phone_number.validate(value):
        raise ValidationError("شماره تلفن نامعتبر است")


# uploads/validators.py
from django.core.exceptions import ValidationError
import magic  # python-magic library for content detection

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": [".pdf"],
    "application/msword": [".doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx"
    ],
    "application/vnd.ms-excel": [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/plain": [".txt"],
    "text/csv": [".csv"],
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
}


def validate_file_type(file, allowed_types):
    """
    Validate file type by checking actual content, not just extension.
    Uses python-magic to detect file MIME type from content.
    """
    # Read first chunk for magic number detection
    initial_position = file.tell()
    file.seek(0)
    file_content = file.read(2048)  # Read first 2KB for detection
    file.seek(initial_position)  # Reset position

    # Detect MIME type from content
    mime = magic.Magic(mime=True)
    detected_type = mime.from_buffer(file_content)

    if detected_type not in allowed_types:
        allowed_extensions = []
        for extensions in allowed_types.values():
            allowed_extensions.extend(extensions)
        raise ValidationError(
            f"Invalid file type. Detected: {detected_type}. "
            f'Allowed extensions: {", ".join(allowed_extensions)}'
        )

    # Verify extension matches content type
    import os

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_types.get(detected_type, []):
        raise ValidationError(
            f"File extension {ext} does not match content type {detected_type}"
        )

    return detected_type


def validate_file_size(file, max_size_mb):
    """Validate that file size is within limits"""
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes

    if file.size > max_size:
        raise ValidationError(
            f"File size ({file.size / (1024*1024):.1f}MB) exceeds "
            f"maximum allowed size ({max_size_mb}MB)"
        )


def validate_image_dimensions(
    file, max_width=4096, max_height=4096, min_width=100, min_height=100
):
    """Validate image dimensions are within acceptable range"""
    from PIL import Image

    try:
        img = Image.open(file)
        width, height = img.size
        file.seek(0)  # Reset file pointer

        if width > max_width or height > max_height:
            raise ValidationError(
                f"Image dimensions ({width}x{height}) exceed maximum "
                f"({max_width}x{max_height})"
            )

        if width < min_width or height < min_height:
            raise ValidationError(
                f"Image dimensions ({width}x{height}) are below minimum "
                f"({min_width}x{min_height})"
            )

    except Exception as e:
        raise ValidationError(f"Could not read image: {str(e)}")


def scan_for_malware(file):
    """
    Scan uploaded file for malware using ClamAV.
    Requires clamd to be installed and running.
    """
    try:
        import clamd

        cd = clamd.ClamdUnixSocket()

        # Reset file position and scan
        file.seek(0)
        result = cd.instream(file)
        file.seek(0)

        # Check scan result
        status, reason = result["stream"]
        if status != "OK":
            raise ValidationError(f"Malware detected: {reason}")

    except ImportError:
        # ClamAV not installed - log warning but continue
        import logging

        logging.warning("ClamAV not available for malware scanning")
    except clamd.ConnectionError:
        import logging

        logging.warning("Could not connect to ClamAV daemon")


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks.
    Removes special characters and limits length.
    """
    import re
    import os

    # Get base name (removes path components)
    filename = os.path.basename(filename)

    # Remove null bytes and path separators
    filename = filename.replace("\x00", "").replace("/", "").replace("\\", "")

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove any non-alphanumeric characters except underscore, hyphen, and dot
    filename = re.sub(r"[^\w\-.]", "", filename)

    # Limit filename length (preserve extension)
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return f"{name}{ext}"
