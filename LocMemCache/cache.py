# -*- coding: utf-8 -*-
"""
Thread-safe in-memory cache backend.
Forked from Django.
"""

import time
import warnings
import threading
from contextlib import contextmanager
try:
    import cPickle as pickle
except ImportError:
    import pickle

# Stub class to ensure not passing in a `timeout` argument results in
# the default timeout
DEFAULT_TIMEOUT = object()

# Cache does not accept keys longer than this.
MAX_KEY_LENGTH = 128

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches = {}
_expire_info = {}
_locks = {}


class RWLock(object):
    """
    Classic implementation of reader-writer lock with preference to writers.

    Readers can access a resource simultaneously.
    Writers get an exclusive access.

    API is self-descriptive:
        reader_enters()
        reader_leaves()
        writer_enters()
        writer_leaves()
    """
    def __init__(self):
        self.mutex = threading.RLock()
        self.can_read = threading.Semaphore(0)
        self.can_write = threading.Semaphore(0)
        self.active_readers = 0
        self.active_writers = 0
        self.waiting_readers = 0
        self.waiting_writers = 0

    def reader_enters(self):
        with self.mutex:
            if self.active_writers == 0 and self.waiting_writers == 0:
                self.active_readers += 1
                self.can_read.release()
            else:
                self.waiting_readers += 1
        self.can_read.acquire()

    def reader_leaves(self):
        with self.mutex:
            self.active_readers -= 1
            if self.active_readers == 0 and self.waiting_writers != 0:
                self.active_writers += 1
                self.waiting_writers -= 1
                self.can_write.release()

    @contextmanager
    def reader(self):
        self.reader_enters()
        try:
            yield
        finally:
            self.reader_leaves()

    def writer_enters(self):
        with self.mutex:
            if self.active_writers == 0 and self.waiting_writers == 0 and self.active_readers == 0:
                self.active_writers += 1
                self.can_write.release()
            else:
                self.waiting_writers += 1
        self.can_write.acquire()

    def writer_leaves(self):
        with self.mutex:
            self.active_writers -= 1
            if self.waiting_writers != 0:
                self.active_writers += 1
                self.waiting_writers -= 1
                self.can_write.release()
            elif self.waiting_readers != 0:
                t = self.waiting_readers
                self.waiting_readers = 0
                self.active_readers += t
                while t > 0:
                    self.can_read.release()
                    t -= 1

    @contextmanager
    def writer(self):
        self.writer_enters()
        try:
            yield
        finally:
            self.writer_leaves()


class CacheKeyWarning(RuntimeWarning):
    pass


@contextmanager
def dummy():
    """A context manager that does nothing special."""
    yield


class LocMemCache(object):
    def __init__(self, name='LOCMEM', key_prefix='LOC', timeout=259200,
                 max_entries=300, cull_frequency=3):

        self._cache = _caches.setdefault(name, {})
        self._expire_info = _expire_info.setdefault(name, {})
        self._lock = _locks.setdefault(name, RWLock())

        self.key_prefix = key_prefix

        if not isinstance(timeout, (int, float)):
            timeout = 259200
        self.default_timeout = int(timeout)

        if not isinstance(max_entries, (int, float)):
            max_entries = 300
        self._max_entries = int(max_entries)

        if not isinstance(cull_frequency, (int, float)):
            cull_frequency = 3
        self._cull_frequency = int(cull_frequency)

    def get_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the timeout value usable by this backend based upon the provided
        timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout == 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = -1
        return None if timeout is None else time.time() + timeout

    def __contains__(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.has_key(key)

    def has_key(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        key = self.make_key(key)
        with self._lock.reader():
            if not self._has_expired(key):
                return True

        with self._lock.writer():
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False

    def validate_key(self, key):
        """
        Warn about keys that would not be portable.
        """
        if len(key) > MAX_KEY_LENGTH:
            warnings.warn('Key `%s` is longer than %s' % (key, MAX_KEY_LENGTH),
                          CacheKeyWarning)
        for char in key:
            if ord(char) < 33 or ord(char) == 127:
                raise ValueError('Cache key contains invalid characters: %r'
                                 % key)

    def make_key(self, key):
        """Constructs the key used by all other methods."""
        _key = '%s::%s' % (self.key_prefix, key)
        self.validate_key(_key)
        return _key

    def keys(self):
        """All cached keys."""
        pre_length = len(self.key_prefix) + 2
        return sorted(k[pre_length:] for k in self._cache.keys()
                      if not self._has_expired(k))

    def _has_expired(self, key):
        exp = self._expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def ttl(self, key):
        """Returns the number of seconds until the key will expire"""
        key = self.make_key(key)
        exp = self._expire_info.get(key, -1)

        if exp is None:
            return

        now = time.time()
        if exp > now:
            return int(exp - now)
        else:
            self._delete(key)

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache)
                      if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT):
        if len(self._cache) >= self._max_entries:
            self._cull()
        self._cache[key] = value
        self._expire_info[key] = self.get_timeout(timeout)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        key = self.make_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock.writer():
            self._set(key, pickled, timeout)

    def add(self, key, value, timeout=DEFAULT_TIMEOUT):
        """
        Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.

        Returns True if the value was stored, False otherwise.
        """
        key = self.make_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock.writer():
            if self._has_expired(key):
                self._set(key, pickled, timeout)
                return True
            return False

    def get(self, key, default=None, acquire_lock=True):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        key = self.make_key(key)
        pickled = None
        with (self._lock.reader() if acquire_lock else dummy()):
            if not self._has_expired(key):
                pickled = self._cache[key]
        if pickled is not None:
            try:
                return pickle.loads(pickled)
            except pickle.PickleError:
                return default

        with (self._lock.writer() if acquire_lock else dummy()):
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key):
        """
        Delete a key from the cache, failing silently.
        """
        key = self.make_key(key)
        with self._lock.writer():
            self._delete(key)

    def get_or_set(self, key, default, timeout=DEFAULT_TIMEOUT):
        """
        Fetch a given key from the cache. If the key does not exist,
        the key is added and set to the default value. If timeout is given,
        that timeout will be used for the key;
        otherwise the default cache timeout will be used.

        Returns the value of the key stored or retrieved on success,
        False on error.
        """
        val = self.get(key)
        if val is None:
            if callable(default):
                default = default()
            val = self.add(key, default, timeout=timeout)
            if val:
                return self.get(key, default)
        return val

    def incr(self, key, delta=1):
        """
        Add delta to value in the cache. If the key does not exist, raise a
        ValueError exception.
        """
        with self._lock.writer():
            value = self.get(key, acquire_lock=False)
            if value is None:
                raise ValueError("Key '%s' not found" % key)
            new_value = value + delta
            key = self.make_key(key)
            pickled = pickle.dumps(new_value, pickle.HIGHEST_PROTOCOL)
            self._cache[key] = pickled
        return new_value

    def decr(self, key, delta=1):
        """
        Subtract delta from value in the cache. If the key does not exist, raise
        a ValueError exception.
        """
        return self.incr(key, -delta)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT):
        """
        Set a bunch of values in the cache at once from a dict of key/value
        pairs.

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        for key, value in data.items():
            self.set(key, value, timeout=timeout)

    def get_many(self, keys):
        """
        Fetch a bunch of keys from the cache.

        Returns a dict mapping each key in keys to its value. If the given
        key is missing, it will be missing from the response dict.
        """
        d = {}
        for k in keys:
            val = self.get(k)
            if val is not None:
                d[k] = val
        return d

    def delete_many(self, keys):
        """
        Delete a bunch of values in the cache at once.
        """
        for key in keys:
            self.delete(key)

    def clear(self):
        """Remove *all* values from the cache at once."""
        self._cache.clear()
        self._expire_info.clear()
