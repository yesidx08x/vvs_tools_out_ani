import os
from diskcache import Cache
from functools import wraps
import marshal as pickle
import hashlib
import inspect

class PipelineCache:

    def __init__(self, cache_dir=None,expire_time=3600000, include_code=False):
        if cache_dir is None:
            home_dir = os.path.expanduser("~")
            cache_dir = os.path.join(home_dir, "stage", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_dir = cache_dir
        self.expire_time = expire_time
        self.include_code = include_code
        self.cache = Cache(cache_dir)

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            refresh = kwargs.pop('__refresh_cache__', False)
            return self._execute(func, args, kwargs, refresh)
        return wrapped

    def _execute(self, func, args, kwargs, refresh):
        key = self._generate_key(func, args, kwargs)

        if refresh and key in self.cache:
            del self.cache[key]

        if key in self.cache:
            return self.cache[key]

        result = func(*args, **kwargs)
        self.cache.set(key, result, expire=self.expire_time)
        return result

    def invalidate(self, *args, **kwargs):
        def decorator(func):
            key = self._generate_key(func, args, kwargs)
            if key in self.cache:
                del self.cache[key]
            return func
        return decorator

    def refresh(self, *args, **kwargs):
        def decorator(func):
            key = self._generate_key(func, args, kwargs)
            result = func(*args, **kwargs)
            self.cache.set(key, result, expire=self.expire_time)
            return result
        return decorator

    def _generate_key(self, func, args, kwargs):
        key_data = [
            func.__module__,
            func.__name__,
            args[1:],
            tuple(sorted(kwargs.items()))
        ]

        if self.include_code:
            try:
                key_data.append(inspect.getsource(func))
            except OSError:
                pass
        serialized = pickle.dumps(key_data)
        return hashlib.sha256(serialized).hexdigest()