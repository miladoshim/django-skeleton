import time
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db import connection
from django.db import reset_queries


def unauthenticated_user(view_func):
    @wraps
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticate:
            return redirect('home_view')
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
                return HttpResponse('you dont have permission')
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
        print('function_name: {}'.format(func.__name__))
        print('query_count: {}'.format(len(query_info)))
        queries = ['{}\n'.format(query['sql']) for query in query_info]
        print('queries: \n{}'.format(''.join(queries)))
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
        if not request.user.is_supperuser:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper