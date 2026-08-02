from .common import *

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USERNAME"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    },
}
STORAGES = {
    "default": {
        # "apps.file_manager.services.storage_service.MediaStorage"
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        # "apps.file_manager.services.storage_service.StaticStorage"
    },
    "import_export": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "sftp": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "HOST": "sftp.example.com",
            "PORT": 22,
            "USERNAME": "username",
            "PASSWORD": "password",
            "REMOTE_PATH": "/path/to/remote/directory",
        },
    },
}

DEFAULT_PROTOCOL = "http"

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CSRF_COOKIE_DOMAIN = "localhost"

# AWS S3 Settings
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="cocopubbucket")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_DEFAULT_ACL = None
WS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "static"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
X_FRAME_OPTIONS = "SAMEORIGIN"

CORS_ALLOW_ALL_ORIGINS = True

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "skeleton_",
        "TIMEOUT": 50,
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "skeleton_select2_",
    },
    "admin_interface": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 5,
    },
}

# Celery Configuration Options Start

CELERY_CACHE_BACKEND = "default"
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_TASK_DEFAULT_QUEUE = "default"

# Celery Configuration Options End


ZEAL_RAISE = False
ZEAL_SHOW_ALL_CALLERS = True

MEILISEARCH = {
    "HOST": "http://localhost:7700",
    "API_KEY": "URoxS-SG7GzbR8UEHY4VBraUm-XBehOuI9BzV26fPTQ",
}


# INSTALLED_APPS = [
#  'daphne',
#  'drf_spectacular'
# ] + INSTALLED_APPS


INSTALLED_APPS.append("zeal")
MIDDLEWARE.append("zeal.middleware.zeal_middleware")
ZEAL_SHOW_ALL_CALLERS = True


CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # آدرس پروژه Vue
]

INTERNAL_IPS = [
    "127.0.0.1",
]
