import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skeleton.settings")
django.setup()

from django.conf import settings
import boto3
from botocore.config import Config

print(
    "AWS_ACCESS_KEY_ID:",
    settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else "NOT SET",
)
print(
    "AWS_SECRET_ACCESS_KEY:",
    settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else "NOT SET",
)
print("AWS_STORAGE_BUCKET_NAME:", settings.AWS_STORAGE_BUCKET_NAME)
print("AWS_S3_ENDPOINT_URL:", settings.AWS_S3_ENDPOINT_URL)


config = Config(
    connect_timeout=30,
    read_timeout=30,
    retries={"max_attempts": 2},
    signature_version="s3v4",
    s3={"addressing_style": "path"},
)

client = boto3.client(
    "s3",
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=config,
)


# مستقیم آپلود کن (بدون HeadBucket)
try:
    #     client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
    #     print("✅ اتصال موفق - bucket وجود دارد")
    client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key="test.txt",
        Body=b"Test file content",
    )
    print("✅ آپلود موفق!")

    # دانلود کن
    response = client.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key="test.txt"
    )
    print(f"✅ دانلود موفق: {response['Body'].read()}")

    # پاک کن
    client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key="test.txt")
    print("✅ پاک کردن موفق")

except Exception as e:
    print(f"❌ خطا: {str(e)}")
    print(f"نوع خطا: {type(e).__name__}")
