import os
import uuid
import hashlib
import boto3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from storages.backends.s3boto3 import S3Boto3Storage
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

StaticRootS3BotoStorage = lambda: S3Boto3Storage(location="static")
MediaRootS3BotoStorage = lambda: S3Boto3Storage(location="media")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def storage_list_files():
    s3_client = get_s3_client()
    try:
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return JsonResponse({"files": files})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def storage_upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        s3_client = get_s3_client()
        file = request.FILES["file"]
        try:
            s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
            return JsonResponse({"message": f"{file.name} uploaded successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


def storage_delete_file(file_name):
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
        )
        return JsonResponse({"message": f"{file_name} deleted successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def generate_presigned_url(request):
    file_name = request.GET.get("file_name")
    if not file_name:
        return JsonResponse({"error": "File name is required"}, status=400)
    s3_client = get_s3_client()
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_name},
            ExpiresIn=3600,  # URL valid for 1 hour
        )
        return JsonResponse({"url": url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def download_file(request):
    file_name = request.GET.get("file_name")
    if not file_name:
        return JsonResponse({"error": "File name is required"}, status=400)
    s3_client = get_s3_client()
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_name},
            ExpiresIn=3600,  # URL valid for 1 hour
        )
        return JsonResponse({"url": url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def unique_filename(instance, filename):
    ext = filename.split(".")[-1]

    new_name = f"{instance._meta.model_name}_{instance.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    if "video" in filename.lower() or "mp4" in ext:
        return f"videos/{new_name}"
    elif "image" in filename.lower() or ext in ["jpg", "png", "jpeg"]:
        return f"images/{new_name}"
    else:
        return f"files/{datetime.now().strftime('%Y/%m/%d')}/{new_name}"


def custom_upload_to(prefix="uploads"):
    """
    تابع通用‌تر برای مسیردهی فایل‌ها
    استفاده: upload_to=custom_upload_to('courses/videos')
    """

    def _upload_to(instance, filename):
        ext = filename.split(".")[-1]
        random_name = f"{uuid.uuid4().hex[:16]}.{ext}"
        return f"{prefix}/{random_name}"

    return _upload_to


def upload_file(file_obj, path_prefix="uploads"):
    """
    سرویس ساده آپلود فایل

    مثال استفاده:
    result = upload_file(request.FILES['file'], 'courses/videos')
    video.video_file = result['path']
    """
    # تولید نام یکتا
    ext = file_obj.name.split(".")[-1]
    new_name = f"{uuid.uuid4().hex[:16]}.{ext}"
    full_path = f"{path_prefix}/{new_name}"

    # محاسبه حجم
    file_content = file_obj.read()
    file_size = len(file_content)

    # ذخیره فایل
    saved_path = default_storage.save(full_path, ContentFile(file_content))

    return {
        "path": saved_path,
        "url": default_storage.url(saved_path),
        "name": new_name,
        "original_name": file_obj.name,
        "size": file_size,
        "checksum": hashlib.sha256(file_content).hexdigest(),
    }


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"
    file_overwrite = False
    querystring_auth = True


class MediaStorage(S3Boto3Storage):
    location = "uploads"
    default_acl = "public-read"
    file_overwrite = False
    custom_domain = settings.MEDIA_URL
    querystring_auth = False


class PublicMediaStorage(S3Boto3Storage):
    location = "uploads/public"
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = "uploads/private"
    default_acl = "private"
    file_overwrite = False
    querystring_auth = True  # لینک‌های زمان‌دار
    querystring_expire = 3600  # 1 ساعت

    def get_queryset_auth(self):
        return True


from typing import Optional, List
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import transaction
from PIL import Image
import os
import uuid
import base64
from io import BytesIO


class FileService:
    """
    سرویس مدیریت فایل‌ها
    استفاده مشترک در Web/API/GraphQL
    """

    def __init__(self):
        self.allowed_images = ["jpg", "jpeg", "png", "gif", "webp"]
        self.allowed_documents = ["pdf", "doc", "docx", "xls", "xlsx", "txt"]
        self.max_file_size = 5 * 1024 * 1024  # 5MB

    def upload_file(self, file, folder: str = "uploads/") -> dict:
        """
        آپلود فایل
        استفاده در: Web upload، API upload، GraphQL upload
        """
        # بررسی حجم فایل
        if file.size > self.max_file_size:
            raise ValueError("حجم فایل نباید بیشتر از 5 مگابایت باشد")

        # بررسی پسوند فایل
        ext = file.name.split(".")[-1].lower()
        if ext not in self.allowed_images + self.allowed_documents:
            raise ValueError("فرمت فایل پشتیبانی نمی‌شود")

        # ساخت نام یکتا
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(folder, filename)

        # اگر عکس است، بهینه‌سازی کن
        if ext in self.allowed_images:
            filepath = self._optimize_image(file, filepath)
        else:
            # ذخیره فایل
            default_storage.save(filepath, ContentFile(file.read()))

        return {
            "file": filepath,
            "url": f"/media/{filepath}",
            "size": file.size,
            "format": ext,
        }

    def upload_base64(self, data: str, folder: str = "uploads/") -> dict:
        """
        آپلود فایل با Base64
        فقط برای API و GraphQL
        """
        try:
            # جدا کردن metadata از data
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            # تبدیل به فایل
            file = ContentFile(base64.b64decode(imgstr))
            file.name = f"file.{ext}"

            return self.upload_file(file, folder)
        except Exception as e:
            raise ValueError("فرمت Base64 نامعتبر است")

    def delete_file(self, filepath: str) -> bool:
        """
        حذف فایل
        استفاده در: Web delete، API delete، GraphQL delete
        """
        try:
            if default_storage.exists(filepath):
                default_storage.delete(filepath)
                return True
            return False
        except Exception:
            return False

    def get_file_url(self, filepath: str) -> str:
        """
        دریافت URL فایل
        استفاده در: Web template، API serializer، GraphQL resolver
        """
        if not filepath:
            return None

        return default_storage.url(filepath)

    def _optimize_image(self, image, filepath: str) -> str:
        """بهینه‌سازی عکس"""
        try:
            img = Image.open(image)

            # تغییر اندازه اگر خیلی بزرگ است
            max_width = 1920
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # ذخیره بهینه
            buffer = BytesIO()
            if img.mode in ("RGBA", "LA"):
                img.save(buffer, format="PNG", optimize=True)
                filepath = (
                    filepath.replace(".jpg", ".png")
                    .replace(".jpeg", ".png")
                    .replace(".webp", ".png")
                )
            else:
                img = img.convert("RGB")
                img.save(buffer, format="JPEG", quality=85, optimize=True)
                filepath = (
                    filepath.replace(".png", ".jpg")
                    .replace(".gif", ".jpg")
                    .replace(".webp", ".jpg")
                )

            # ذخیره فایل
            default_storage.save(filepath, ContentFile(buffer.getvalue()))
            return filepath

        except Exception as e:
            # اگر بهینه‌سازی نشد، فایل اصلی را ذخیره کن
            image.seek(0)
            default_storage.save(filepath, ContentFile(image.read()))
            return filepath
