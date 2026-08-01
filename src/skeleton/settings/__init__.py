import os

from decouple import config

from .common import *

env = config("APP_ENV", default="production")

if env == "production":
    from .production import *
elif env == "development":
    from .development import *
else:
    raise ValueError("Invalid APP_ENV")
