# coding=utf-8


class _CacheType(object):
    Add = 1
    Sub = 2
    Destroy = 3


class Event(object):
    __slots__ = '_destroyed', '_listeners', '_firing', '_cache'

    def __init__(self):
        self._destroyed = False
        self._listeners = set()
        self._firing = False
        self._cache = []

    def __iadd__(self, other):
        if self._destroyed:
            return self
        if self._firing:
            self._cache.append((_CacheType.Add, other))
            return self
        self._listeners.add(other)
        return self

    def __isub__(self, other):
        if self._firing:
            self._cache.append((_CacheType.Sub, other))
            return self
        self._listeners.discard(other)
        return self

    def __call__(self, *args, **kwargs):
        self.fire(*args, **kwargs)

    def fire(self, *args, **kwargs):
        if self._destroyed:
            return

        self._firing = True
        for listener in self._listeners:
            try:
                listener(*args, **kwargs)
            except Exception:
                # TODO: traceback
                import traceback
                traceback.print_exc()
        self._firing = False
        self._process_cache()

    def _process_cache(self):
        call_destroy = False
        for cache_type, listener in self._cache:
            if cache_type == _CacheType.Add:
                self._listeners.add(listener)
            elif cache_type == _CacheType.Sub:
                self._listeners.discard(listener)
            elif cache_type == _CacheType.Destroy:
                call_destroy = True
        self._cache = []
        call_destroy and self.destroy()

    def destroy(self):
        if self._firing:
            self._cache.append((_CacheType.Destroy, None))
            return
        self._listeners.clear()
        self._destroyed = True
