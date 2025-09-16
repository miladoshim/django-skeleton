import time
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import PermissionDenied
from functools import wraps


def get_ckeditor_filename(filename, request):
    return filename.upper()


def superuser_only(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_supperuser:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper


def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        starttime = time.time()
        value = func(*args, **kwargs)
        endtime = time.time()
        print(f"func name: {func.__name__} take time: {endtime - starttime}")
        return value

    return wrapper


def time_of_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t_s = time.time()
        result = func(*args, **kwargs)
        t_e = time.time()
        print(func.__name__, t_s - t_e)
        return result

    return wrapper


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()
