import time
from functools import wraps
from django.db import connection, reset_queries
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def anonymous_required(redirect_url):
    def _wrapped(view_func, *args, **kwargs):
        def check_anonymous(request, *args, **kwargs):
            view = view_func(request, *args, **kwargs)
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view

        return check_anonymous

    return _wrapped


def unauthenticated_user(view_func):
    @wraps
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticate:
            return redirect("apps.pages:home_view")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps
        def wrapper(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("you dont have permission")

        return wrapper

    return decorator


def database_debug(func):
    @wraps
    def wrapper(*args, **kwargs):
        reset_queries()
        results = func()
        query_info = connection.queries
        st = time.time()
        et = time.time()
        print("function_name: {}".format(func.__name__))
        print("query_count: {}".format(len(query_info)))
        queries = ["{}\n".format(query["sql"]) for query in query_info]
        print("queries: \n{}".format("".join(queries)))
        print(f"take time : {(st - et):.3f}")
        return results

    return wrapper


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


def superuser_only(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper


def login_role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if required_role == "coach" and not user.is_coach:
                return HttpResponseForbidden("you dont access")
            return view_func(request, *args, **kwargs)
