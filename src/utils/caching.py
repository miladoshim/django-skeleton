from django.core.cache import cache


class Caching:
    @staticmethod
    def set(key, value, timeout: int = 200):
        cache.set(key, value, timeout=timeout)

    def get(key):
        return cache.get(key)

    def delete(key):
        return cache.delete(key)

    def exists(key):
        return cache.has_key(key)

    def set_many(timeout: int = 200, **kwargs):
        return cache.set_many(**kwargs, timeout=timeout)

    def get_many(*args):
        return cache.get_many(*args)
