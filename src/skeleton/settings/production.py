import os
import dj_database_url
from decouple import config
from .common import *

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", ""),
        conn_health_checks=True,
        engine="django.db.backends.postgresql_psycopg2",
    ),
}

STORAGES = {
    "default": {
        # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "BACKEND": "apps.core.services.storage_service.MediaStorage"
    },
    "staticfiles": {
        "BACKEND": "apps.core.services.storage_service.StaticStorage",
        # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "import_export": {
        # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "BACKEND": "apps.core.services.storage_service.MediaStorage",
    },
}

DEFAULT_PROTOCOL = "https"

AWS_ACCESS_KEY_ID = config(
    "AWS_ACCESS_KEY_ID",
    default="553cb5cpotimkser",
)
AWS_SECRET_ACCESS_KEY = config(
    "AWS_SECRET_ACCESS_KEY",
    default="6f684937-04e3-4e35-9614-a3bb387b8155",
)
AWS_STORAGE_BUCKET_NAME = config(
    "AWS_STORAGE_BUCKET_NAME",
    default="cocoplbucket",
)
AWS_S3_ENDPOINT_URL = config(
    "AWS_S3_ENDPOINT_URL",
    default="https://storage.c2.liara.site",
)
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_LOCATION = "uploads"
AWS_STATIC_LOCATION = "static"
AWS_S3_CUSTOM_DOMAIN = "storage.skeleton.ir"
AWS_S3_USE_SSL = True
AWS_S3_VERIFY = True
AWS_S3_CHECK_BUCKET = False
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = "public-read"

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_DOMAIN = ".skeleton.ir"
CSRF_USE_SESSIONS = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 ساعت

CSRF_TRUSTED_ORIGINS = [
    "http://skeleton.ir",
    "https://skeleton.ir",
    "https://*.skeleton.ir",
]

WHITENOISE_USE_HTTPS = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = config("MAIL_PORT", cast=int, default=556)
EMAIL_HOST_USER = config("MAIL_USER", default="")
EMAIL_HOST_PASSWORD = config("MAIL_PASSWORD", default="")
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default=""),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "skeleton_",
        "TIMEOUT": 300,
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("SELECT2_CACHE_URL", default=""),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "skeleton_select2_",
    },
    "admin_interface": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default=""),
        "TIMEOUT": 60 * 5,
        "KEY_PREFIX": "skeleton_admin_interface_",
    },
}


# Celery Configuration Options Start

CELERY_CACHE_BACKEND = "default"
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="")
CELERY_TASK_DEFAULT_QUEUE = "default"

# Celery Configuration Options End


CACHEOPS_REDIS = "redis://:Iei608rSW7HyqMv3g3U665Ah@cocoredis:6379/0"
CACHEOPS_ENABLED = True

CORS_ALLOWED_ORIGINS = [
    "http://skeleton.ir",
    "https://skeleton.ir",
    "https://*.skeleton.ir",
]
