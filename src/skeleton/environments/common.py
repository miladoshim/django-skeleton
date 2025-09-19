from import_export.formats.base_formats import CSV, XLSX
import os
import locale
import sys
from pathlib import Path
from django.conf import settings
from os.path import join
from decouple import config
from django_components import ComponentsSettings

PROJECT_ROOT = os.path.dirname(__file__)

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = str(BASE_BASE_DIR.joinpath("templates/skeleton/"))

sys.path.insert(0, join(PROJECT_ROOT, "apps"))


# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

SECRET_KEY = "django-insecure-^q52bhy0%%xi(h9rf4ow=7h*^$8y49+g+ig#8_hx7fnba-i^h*"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# SECURE_SSL_REDIRECT=True

INSTALLED_APPS = [
    "daphne",
    "django.contrib.contenttypes",
    # 'grappelli.dashboard',
    # 'grappelli',
    "admin_interface",
    "colorfield",
    "filebrowser",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django.contrib.postgres",
    # Local apps
    "apps.core.apps.CoreConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.blog.apps.BlogConfig",
    "apps.api.apps.ApiConfig",
    # Third-party apps
    "channels",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "import_export",
    "debug_toolbar",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "guardian",
    "csp",
    "django_extensions",
    "hitcount",
    "meta",
    "django_filters",
    "drf_api_logger",
    "django_guid",
    "taggit",
    "compressor",
    "django_components",
    "jalali_date",
    "crispy_forms",
    "crispy_tailwind",
    "treebeard",
    'auditlog',
    "ckeditor",
    "ckeditor_uploader",
    "extra_settings",
    'pwa',
    # 'redirects',
    "django_unicorn",
    "utils",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    # "django.middleware.cache.UpdateCacheMiddleware",
    "django_guid.middleware.guid_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'django.middleware.locale.LocaleMiddleware'
    # "django.middleware.cache.FetchFromCacheMiddleware",
    # Local middlewares
    # Third-party middlewares
    "csp.middleware.CSPMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware",
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = "skeleton.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        # Default Django loader
                        "django.template.loaders.filesystem.Loader",
                        # Including this is the same as APP_DIRS=True
                        "django.template.loaders.app_directories.Loader",
                        # Components loader
                        "django_components.template_loader.Loader",
                    ],
                )
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]

# COMPONENTS = ComponentsSettings(
#     app_dirs=[
#         # ...,
#         "components",
#     ],
# )
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # this is default
    "guardian.backends.ObjectPermissionBackend",
)

WSGI_APPLICATION = "skeleton.wsgi.application"
ASGI_APPLICATION = "skeleton.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "postgres": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USERNAME"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    },
}

# DATABASE_ROUTERS=['routers.db_routers.AuthRouter']

INTERNAL_IPS = [
    "127.0.0.1",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization

LANGUAGE_CODE = "fa-IR"

TIME_ZONE = "Asia/Tehran"

if sys.platform.startswith("win32"):
    locale.setlocale(locale.LC_ALL, "Persian_Iran.UTF-8")
else:
    locale.setlocale(locale.LC_ALL, "fa_IR.UTF-8")

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [str(BASE_BASE_DIR.joinpath("static/skeleton/"))]

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_FILENAME_GENERATOR = 'utils.get_ckeditor_filename'
CKEDITOR_RESTRICT_BY_DATE = True
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline"],
            [
                "NumberedList",
                "BulletedList",
                "-",
                "Outdent",
                "Indent",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
            ],
            ["Link", "Unlink"],
            ["RemoveFormat", "Source"],
        ],
        "extraPlugins": ",".join(
            [
                "uploadimage",
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # 'devtools',
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
        # 'height': 300,
        # 'width': 300,
    },
}

FILEBROWSER_DIRECTORY = "/uploads"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
    "django_components.finders.ComponentsFileSystemFinder",
)

LOGIN_REDIRECT_URL = "home_view"
LOGOUT_REDIRECT_URL = "home_view"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

DEFAULT_FROM_EMAIL = "info@skeleton.com"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", "localhost")
EMAIL_POST = config("EMAIL_PORT", 25)
# EMAIL_HOST_USER = config('EMAIL_HOST')
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.TokenAuthentication',
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
}

DRF_API_LOGGER_DATABASE = True
DRF_API_LOGGER_SIGNAL = False

SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "TITLE": "skeleton API",
    "DESCRIPTION": "Your project description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://django@localhost:6379/0",
        # "LOCATION": "redis://127.0.0.1:6379/1",
        # "OPTIONS": {
        #     "CLIENT_CLASS": "django_redis.client.DefaultClient",
        #     "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        #     "PASSWORD": "mysecret",
        # "IGNORE_EXCEPTIONS": True,
        # }
    },
    "admin_interface": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 5,
    },
}

# LOGGING = {
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         }
#     },
# }

JALALI_DATE_DEFAULTS = {
    "LIST_DISPLAY_AUTO_CONVERT": True,
    "Strftime": {
        "date": "%y/%m/%d",
        "datetime": "%H:%M:%S _ %y/%m/%d",
    },
    "Static": {
        "js": [
            "admin/js/django_jalali.min.js",
            # OR
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
            # 'admin/js/main.js',
        ],
        "css": {
            "all": [
                "admin/css/django_jalali.min.css",
                # "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
            ]
        },
    },
}

IMPORT_EXPORT_FORMATS = [CSV, XLSX]

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
# CELERY_BROKER_URL = broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_DEFAULT_QUEUE = "default"

TAGGIT_CASE_INSENSITIVE = True

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"


AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": "<YOUR MERCHANT CODE>",
            "SANDBOX": 1,  # 0 disable, 1 active
        },
        "IDPAY": {
            "MERCHANT_CODE": "<YOUR MERCHANT CODE>",
            "METHOD": "POST",  # GET or POST
            "X_SANDBOX": 1,  # 0 disable, 1 active
        },
    },
    "IS_SAMPLE_FORM_ENABLE": True,  # اختیاری و پیش فرض غیر فعال است
    "DEFAULT": "ZARINPAL",
    "CURRENCY": "IRT",  # اختیاری
    "TRACKING_CODE_QUERY_PARAM": "tc",  # اختیاری
    "TRACKING_CODE_LENGTH": 16,  # اختیاری
    "SETTING_VALUE_READER_CLASS": "azbankgateways.readers.DefaultReader",  # اختیاری
    "BANK_PRIORITIES": [
        "ZARINPAL",
        "IDPAY",
    ],  # اختیاری
    "IS_SAFE_GET_GATEWAY_PAYMENT": True,  # اختیاری، بهتر است True بزارید.
    "CUSTOM_APP": None,  # اختیاری
}

# CORS_ALLOWED_ORIGINS = [
#     "https://frontend.com",
#     "http://localhost:3000",
# ]

CORS_ALLOW_ALL_ORIGINS = True

# ELASTICSEARCH_DSL = {
#     "default": {"hosts": "elasticsearch:9200"},
# }

PWA_APP_NAME = 'Skeleton'
PWA_APP_DESCRIPTION = "Skeleton description"
PWA_APP_THEME_COLOR = '#0A0302'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_DEBUG_MODE=True
# PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'my_app', 'serviceworker.js')
PWA_APP_ICONS = [
    {
        'src': '/static/images/my_app_icon.png',
        'sizes': '160x160'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/images/my_apple_icon.png',
        'sizes': '160x160'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/icons/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'fa-IR'
PWA_APP_SHORTCUTS = [
    {
        'name': 'Shortcut',
        'url': '/target',
        'description': 'Shortcut to a page in my application'
    }
]
PWA_APP_SCREENSHOTS = [
    {
      'src': '/static/images/icons/splash-750x1334.png',
      'sizes': '750x1334',
      "type": "image/png"
    }
]