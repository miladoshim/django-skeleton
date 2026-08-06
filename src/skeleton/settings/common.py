import os
import sys
from datetime import timedelta
from os.path import join
from pathlib import Path
from decouple import config
from django.contrib import messages
from django_guid.integrations import CeleryIntegration
from import_export.formats.base_formats import CSV, XLSX

PROJECT_ROOT = os.path.dirname(__file__)

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = str(BASE_BASE_DIR.joinpath("templates/skeleton/"))

DEBUG = config("DEBUG", default=False, cast=bool)

TESTING = "test" in sys.argv or "PYTEST_VERSION" in os.environ

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="*",
)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")
STATICFILES_DIRS = [
    BASE_BASE_DIR.joinpath("static/skeleton/"),
]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # "compressor.finders.CompressorFinder",
)


WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_INDEX_FILE = True


sys.path.insert(0, join(PROJECT_ROOT, "apps"))

SECRET_KEY = config("SECRET_KEY", default="")

DOMAIN = config("APP_DOMAIN", default="skeleton.ir")
SITE_NAME = config("APP_NAME", default="کوکوند")
SITE_ID = 1

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.contenttypes",
    "admin_interface",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "apps.core.apps.CoreConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.blog.apps.BlogConfig",
    "apps.api.apps.ApiConfig",
    "apps.financial.apps.FinancialConfig",
    "apps.pages.apps.PagesConfig",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "import_export",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "drf_api_logger",
    "robots",
    "hitcount",
    "meta",
    "django_extensions",
    "django_filters",
    "storages",
    "django_guid",
    "taggit",
    "taggit_labels",
    "taggit_selectize",
    "matomo",
    "django_minify_html",
    "crispy_forms",
    "django_cotton",
    "pwa",
    "colorfield",
    "redirects",
    "django_celery_results",
    "django_celery_beat",
    "azbankgateways",
    "debug_toolbar",
    "iranian_cities",
    "cache_cleaner",
    "schema_viewer",
    "star_ratings",
    "django_admin_trap",
    "utils",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django_guid.middleware.guid_middleware",
    "redirects.middleware.RedirectMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware",
    "django_minify_html.middleware.MinifyHtmlMiddleware",
    "apps.core.middlewares.RequestIdMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

if DEBUG:
    print("DEBUG MODE")
else:
    print("PRODUCTION MODE")


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
                # "js_asset.context_processors.importmap",
                "apps.core.context_processors.global_variables",
            ],
            "builtins": [
                "django_cotton.templatetags.cotton",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django_cotton.cotton_loader.Loader",
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# WSGI_APPLICATION = "skeleton.wsgi.application"
ASGI_APPLICATION = "skeleton.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

ROBOTS_USE_HOST = False
ROBOTS_USE_SITEMAP = False

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

LANGUAGE_CODE = "fa-IR"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = "apps.pages:home_view"
LOGIN_URL = "apps.accounts:login_view"
LOGOUT_REDIRECT_URL = "apps.pages:home_view"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
USE_DJANGO_JQUERY = True
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
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
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_CACHE_KEY_DEFAULT_PERMISSIONS": [],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
    "EXCEPTION_HANDLER": "utils.exception_handler.custom_exception_handler",
}

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_BLACKLIST_ENABLED": True,
}


DJANGO_CLEANUP = {
    "EXCLUDE": ("*.tmp",),
}

ORPHAN_FILES_CLEANUP = {
    "SCAN_DIRS": [],
    "IGNORE_DIRS": ["cache", "tmp"],
    "IGNORE_FILES": [
        ".gitkeep",
        "default_man_avatar.jpg",
        "courses/thumbnails/2026/05/25/4.jpg",
    ],
    "MIN_AGE_HOURS": 24,
}

SPECTACULAR_SETTINGS = {
    "VERSION": "1.0.0",
    "TITLE": "skeleton API V1",
    "DESCRIPTION": "skeleton api project",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_INCLUDE_SCHEMA": False,
}

CACHE_MIDDLEWARE_SECONDS = 60

COMPRESS_ENABLED = True

MAIL_FROM = "skeleton <info@skeleton.ir>"
DEFAULT_FROM_EMAIL = "info@skeleton.ir"
MAIL_FROM_ADDRESS = "info@skeleton.ir"

# JALALI_DATE_DEFAULTS = {
#     "LIST_DISPLAY_AUTO_CONVERT": True,
#     "Strftime": {
#         "date": "%y/%m/%d",
#         "datetime": "%H:%M:%S _ %y/%m/%d",
#     },
#     "Static": {
#         "js": [
#             "admin/js/django_jalali.min.js",
#             # OR
#             # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
#             # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
#             # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
#             # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
#             # 'admin/js/main.js',
#         ],
#         "css": {
#             "all": [
#                 "admin/css/django_jalali.min.css",
#                 # "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
#             ]
#         },
#     },
# }

SILKY_PYTHON_PROFILER = True

IMPORT_EXPORT_FORMATS = [CSV, XLSX]

GUNICORN_MAX_REQUESTS = 2000


DRF_API_LOGGER_DATABASE = False
DRF_API_LOGGER_SIGNAL = True
# DRF_API_LOGGER_DEFAULT_DATABASE = "api_logs_db"
DRF_LOGGER_QUEUE_MAX_SIZE = 100
DRF_LOGGER_INTERVAL = 5
DRF_API_LOGGER_SLOW_API_ABOVE = 200
DRF_API_LOGGER_MAX_REQUEST_BODY_SIZE = 32768
DRF_API_LOGGER_MAX_RESPONSE_BODY_SIZE = 65536
# CREATE INDEX idx_api_logs_added_on ON drf_api_logs(added_on);
# CREATE INDEX idx_api_logs_api_method ON drf_api_logs(api, method);
LOG_DIR = os.path.join(BASE_DIR, "logs")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "default": "django_guid",
    "filters": {
        "correlation_id": {
            "()": "django_guid.log_filters.CorrelationId",
        },
        "celery_tracing": {
            "()": "django_guid.integrations.celery.log_filters.CeleryTracing"
        },
        "request_filter": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: record.name != "django.request"
            or record.levelname != "INFO",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "medium",
            "filters": ["correlation_id", "celery_tracing"],
        },
        "daily_file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR + "/system.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
            "formatter": "medium",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR + "/errors.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 14,
            "formatter": "medium",
        },
    },
    "formatters": {
        "medium": {
            "format": "%(levelname)s [%(correlation_id)s] [%(celery_parent_id)s-%(celery_current_id)s] %(name)s - %(message)s"
        }
    },
    "loggers": {
        "django_guid": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "import_export": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

DJANGO_GUID = {
    "INTEGRATIONS": [
        # SentryIntegration(),
        CeleryIntegration(
            use_django_logging=True,
            log_parent=True,
        ),
    ],
}


TAGGIT_CASE_INSENSITIVE = True
TAGGIT_TAGS_FROM_STRING = "taggit_selectize.utils.parse_tags"
TAGGIT_STRING_FROM_TAGS = "taggit_selectize.utils.join_tags"

TAGGIT_SELECTIZE = {
    "MINIMUM_QUERY_LENGTH": 2,
    "RECOMMENDATION_LIMIT": 10,
    "CSS_FILENAMES": ("taggit_selectize/css/selectize.django.css",),
    "JS_FILENAMES": ("taggit_selectize/js/selectize.js",),
    "DIACRITICS": True,
    "CREATE": True,
    "PERSIST": True,
    "OPEN_ON_FOCUS": True,
    "HIDE_SELECTED": True,
    "CLOSE_AFTER_SELECT": False,
    "LOAD_THROTTLE": 300,
    "PRELOAD": False,
    "ADD_PRECEDENCE": False,
    "SELECT_ON_TAB": False,
    "REMOVE_BUTTON": False,
    "RESTORE_ON_BACKSPACE": False,
    "DRAG_DROP": False,
    "DELIMITER": ",",
}

SILENCED_SYSTEM_CHECKS = ["security.W019"]
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_CACHE_ALIAS = "default"
CORS_ALLOW_CREDENTIALS = True


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

MAINTENANCE_MODE = config("MAINTENANCE_MODE", cast=bool, default=False)

SELECT2_CACHE_BACKEND = "select2"

CACHE_TTL = 300

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": config(
                "ZARINPAL_MERCHANT_CODE",
                default="2dd0c58b-35a3-4369-869f-15e5133041ab",
            ),
            "SANDBOX": config("ZARINPAL_SANDBOX", default=True, cast=bool),
        },
    },
    "IS_SAMPLE_FORM_ENABLE": True,
    "DEFAULT": "ZARINPAL",
    "CURRENCY": "IRT",
    "TRACKING_CODE_QUERY_PARAM": "tc",
    "TRACKING_CODE_LENGTH": 16,
    "SETTING_VALUE_READER_CLASS": "azbankgateways.readers.DefaultReader",
    "IS_SAFE_GET_GATEWAY_PAYMENT": True,
}


KAVENEGAR_API_KEY = config("KAVENEGAR_API_KEY", default="")
KAVENEGAR_SENDER = config("KAVENEGAR_SENDER", cast=int, default=1)
KAVENEGAR_OTP_TEMPLATE = config("KAVENEGAR_OTP_TEMPLATE", default="otp")


# PWA Setting Start

PWA_APP_NAME = config("APP_NAME", default="skeleton")
PWA_APP_DESCRIPTION = config("APP_DESCRIPTION", default="skeleton Application")
PWA_APP_THEME_COLOR = "#6a1e55"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_APP_DEBUG_MODE = config("PWA_APP_DEBUG_MODE", cast=bool, default=True)
# PWA_SERVICE_WORKER_PATH = os.path.join(BASE_BASE_DIR, "serviceworker.js")
# PWA_APP_ICONS = [{"src": "/static/images/my_app_icon.png", "sizes": "160x160"}]
# PWA_APP_ICONS_APPLE = [{"src": "/static/images/my_apple_icon.png", "sizes": "160x160"}]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/images/icons/splash-640x1136.png",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]
PWA_APP_DIR = "rtl"
PWA_APP_LANG = "fa-IR"
PWA_APP_SHORTCUTS = [
    {
        "name": "Shortcut",
        "url": "/academy/courses",
        "description": "آکادمی",
    }
]
PWA_APP_SCREENSHOTS = [
    {
        "src": "/static/images/icons/splash-750x1334.png",
        "sizes": "750x1334",
        "type": "image/png",
    }
]

# PWA Setting End

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

IRANIAN_CITIES_ADMIN_ADD_READONLY_ENABLED = False
IRANIAN_CITIES_ADMIN_DELETE_READONLY_ENABLED = False
IRANIAN_CITIES_ADMIN_CHANGE_READONLY_ENABLED = True
IRANIAN_CITIES_ADMIN_INLINE_ENABLED = False


CART_SESSION_ID = ""

FIXTURE_DIRS = [
    "fixtures",
]

customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "fa",
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "subscript",
                "superscript",
                "highlight",
                "fontSize",
                "fontColor",
                "fontBackgroundColor",
                "removeFormat",
                "insertTable",
                "|",
                "outdent",
                "indent",
                "|",
                "bulletedList",
                "numberedList",
                "blockQuote",
                "todoList",
                "insertImage",
                "mediaEmbed",
            ],
            "shouldNotGroupWhenFull": "true",
        },
    },
    "extends": {
        "language": "fa",
        "blockToolbar": [
            "heading1",
            "heading2",
            "heading3",
            "paragraph",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": {
            "items": [
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "code",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "insertImage",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "blockQuote",
                "imageUpload",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "mediaEmbed",
                "removeFormat",
                "insertTable",
            ],
            "shouldNotGroupWhenFull": "true",
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_BACKEND = "django-db"

AWS_IS_GZIPPED = True
AWS_QUERYSTRING_EXPIRE = 3600
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 مگابایت
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000
FILE_UPLOAD_PERMISSIONS = 0o644  # File permissions for uploaded files
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # Directory permissions
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

MATOMO_URL = config("MATOMO_URL", default="")
MATOMO_SITE_ID = config("MATOMO_SITE_ID", cast=int, default=1)


ATOMIC_REQUESTS = True
