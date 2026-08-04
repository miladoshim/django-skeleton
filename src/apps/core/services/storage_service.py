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
