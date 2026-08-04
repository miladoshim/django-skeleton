import logging
import os
import uuid
import ffmpeg
import sys
import hashlib
import json
from io import BytesIO
from PIL import Image
from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def process_image(file_path):
    output_file = f"media/images/{uuid.uuid4()}.webp"
    ffmpeg.input(file_path).filter("scale", 1920, 1080).output(
        output_file, compression_level=6
    ).run()
    return output_file


def make_thumbnail(self, image, size=(300, 300)):
    img = Image.open(image)
    img.convert("RGB")
    img.thumbnail(size)
    thumb_io = BytesIO()
    img.save(thumb_io, "JPEG", quality=85)
    thumbnail = File(thumb_io, name=image.name)
    return thumbnail


def convert_to_webp(image_path):
    webp_image_path = image_path.rsplit(".", 1)[0] + ".webp"

    if not os.path.exists(webp_image_path):
        try:
            img = Image.open(image_path)
            img.save(webp_image_path, "WEBP")
            logging.debug(f"Converted {image_path} to WebP.")
        except Exception as e:
            logging.debug(f"Could not convert {image_path} to WebP. Error: {e}")


def resize_image(image_file, max_width=800, max_height=800, quality=85):
    """
    Resize image while maintaining aspect ratio.
    Returns a new InMemoryUploadedFile.
    """
    img = Image.open(image_file)

    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Calculate new dimensions maintaining aspect ratio
    width, height = img.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Save to buffer
    output = BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)

    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        "ImageField",
        f'{image_file.name.rsplit(".", 1)[0]}.jpg',
        "image/jpeg",
        sys.getsizeof(output),
        None,
    )


def create_thumbnail(image_file, size=(150, 150)):
    """
    Create a square thumbnail from an image.
    Crops to center and resizes.
    """
    img = Image.open(image_file)

    # Convert to RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Crop to square (center crop)
    width, height = img.size
    if width != height:
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))

    # Resize to thumbnail
    img.thumbnail(size, Image.Resampling.LANCZOS)

    # Save to buffer
    output = BytesIO()
    img.save(output, format="JPEG", quality=80)
    output.seek(0)

    return InMemoryUploadedFile(
        output,
        "ImageField",
        f'thumb_{image_file.name.rsplit(".", 1)[0]}.jpg',
        "image/jpeg",
        sys.getsizeof(output),
        None,
    )


def extract_image_metadata(image_file):
    """Extract EXIF and other metadata from image"""
    img = Image.open(image_file)

    metadata = {
        "width": img.width,
        "height": img.height,
        "format": img.format,
        "mode": img.mode,
    }

    # Extract EXIF data if available
    exif = img._getexif()
    if exif:
        from PIL.ExifTags import TAGS

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ["DateTimeOriginal", "Make", "Model", "Orientation"]:
                metadata[tag] = value

    image_file.seek(0)
    return metadata


class ImageProcessingError(Exception):
    """خطای اختصاصی پردازش تصویر"""

    pass


class ImageService:
    DEFAULT_QUALITY = 85
    DEFAULT_FORMAT = "WEBP"
    SUPPORTED_FORMATS = {"WEBP", "JPEG", "PNG"}
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB

    @classmethod
    def process_image(cls, image_field, sizes=None, quality=None, output_format=None):
        """
        Args:
            image_field: فیلد تصویر Django (FileField/ImageField)
            sizes: دیکشنری سایزها {'small': (300, 300)}
            quality: کیفیت خروجی (1-100)
            output_format: فرمت خروجی (WEBP, JPEG, PNG)
        """
        if not image_field:
            return

        quality = quality or cls.DEFAULT_QUALITY
        output_format = (output_format or cls.DEFAULT_FORMAT).upper()

        if output_format not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"فرمت {output_format} پشتیبانی نمی‌شود")

        try:
            if image_field.size > cls.MAX_IMAGE_SIZE:
                raise ImageProcessingError(f"حجم فایل بیشتر از حد مجاز است")

            # خواندن تصویر از استورج
            img_data = image_field.read()
            img = Image.open(BytesIO(img_data))

            results = {}

            original_result = cls._optimize_original(
                image_field,
                img,
                quality,
                output_format,
            )
            if original_result:
                results["original"] = original_result

            # تولید سایزهای مختلف
            if sizes:
                for size_name, size in sizes.items():
                    size_result = cls._resize_and_save(
                        image_field, img, size_name, size, quality, output_format
                    )
                    if size_result:
                        results[size_name] = size_result

            img.close()

            logger.info(f"تصویر {image_field.name} با موفقیت پردازش شد")
            return results

        except ImageProcessingError as e:
            logger.error(f"خطا در پردازش تصویر: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در پردازش تصویر: {str(e)}")
            raise ImageProcessingError(f"خطا در پردازش تصویر: {str(e)}")

    @classmethod
    def _prepare_image(cls, img):
        if img.mode in ("RGBA", "LA", "P"):
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            else:
                img = img.convert("RGBA")
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        return img

    @classmethod
    def _resize_and_save(
        cls, image_field, img, size_name, size, quality, output_format
    ):
        try:
            img_copy = img.copy()
            img_copy = cls._prepare_image(img_copy)

            img_copy.thumbnail(size, Image.LANCZOS)

            base_name = os.path.splitext(os.path.basename(image_field.name))[0]
            ext = f".{output_format.lower()}"

            # ایجاد مسیر با prefix
            prefix = f"processed/{size_name}/"
            new_name = f"{prefix}{base_name}{ext}"

            buffer = BytesIO()
            save_kwargs = {
                "format": output_format,
                "quality": quality,
                "optimize": True,
            }

            if output_format == "WEBP":
                save_kwargs["method"] = 6

            img_copy.save(buffer, **save_kwargs)
            buffer.seek(0)

            # آپلود به استورج ابری (لیارا)
            saved_path = default_storage.save(new_name, ContentFile(buffer.getvalue()))

            img_copy.close()
            buffer.close()

            return {
                "path": saved_path,
                "url": default_storage.url(saved_path),
                "size": default_storage.size(saved_path),
            }

        except Exception as e:
            logger.error(f"خطا در تغییر سایز {size_name}: {str(e)}")
            return None

    @classmethod
    def _optimize_original(cls, image_field, img, quality, output_format):
        """بهینه‌سازی تصویر اصلی در استورج"""
        try:
            # اگر فرمت اصلی با خروجی یکی است، نیازی به تبدیل نیست
            original_ext = os.path.splitext(image_field.name)[1].lower()
            if original_ext == f".{output_format.lower()}":
                return None

            img = cls._prepare_image(img)

            # تولید نام جدید
            base_name = os.path.splitext(os.path.basename(image_field.name))[0]
            ext = f".{output_format.lower()}"
            new_name = f"optimized/{base_name}{ext}"

            # ذخیره در بافر
            buffer = BytesIO()
            save_kwargs = {
                "format": output_format,
                "quality": quality,
                "optimize": True,
            }

            if output_format == "WEBP":
                save_kwargs["method"] = 6

            img.save(buffer, **save_kwargs)
            buffer.seek(0)

            # آپلود به استورج
            saved_path = default_storage.save(new_name, ContentFile(buffer.getvalue()))

            # حذف فایل اصلی (اختیاری)
            # default_storage.delete(image_field.name)

            buffer.close()

            return {
                "path": saved_path,
                "url": default_storage.url(saved_path),
                "size": default_storage.size(saved_path),
            }

        except Exception as e:
            logger.error(f"خطا در بهینه‌سازی تصویر اصلی: {str(e)}")
            return None

    @classmethod
    def get_image_url(cls, image_field, size_name=None, base_path="processed"):
        """دریافت URL تصویر با سایز مشخص"""
        if not image_field:
            return None

        base_name = os.path.splitext(os.path.basename(image_field.name))[0]

        if size_name:
            path = f"{base_path}/{size_name}/{base_name}.webp"
        else:
            path = f"optimized/{base_name}.webp"

        # بررسی وجود فایل
        if default_storage.exists(path):
            return default_storage.url(path)

        # fallback به تصویر اصلی
        return image_field.url

    @classmethod
    def get_image_info(cls, image_field):
        """دریافت اطلاعات تصویر"""
        if not image_field:
            return None

        try:
            img_data = image_field.read()
            img = Image.open(BytesIO(img_data))

            info = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size": image_field.size,
            }

            img.close()
            return info

        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات تصویر: {str(e)}")
            return None


class ImageSizePresets:
    """سایزهای استاندارد برای انواع محتوا"""

    # محصولات
    PRODUCT = {
        "thumbnail": (150, 150),
        "small": (300, 300),
        "medium": (600, 600),
        "large": (1200, 1200),
    }

    # پروفایل کاربران
    AVATAR = {
        "small": (64, 64),
        "medium": (150, 150),
        "large": (300, 300),
    }

    # دوره‌های آموزشی
    COURSE = {
        "thumbnail": (200, 200),
        "small": (400, 400),
        "medium": (800, 800),
    }

    # مقالات وبلاگ
    BLOG = {
        "thumbnail": (150, 150),
        "medium": (750, 450),
        "large": (1200, 800),
    }
