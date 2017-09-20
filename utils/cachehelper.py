import datetime
import threading


class CacheRepository(object):

    CACHES = {}

    DATE = None # check the date, if it was not equal to today, clear() the expired cache.

    @staticmethod
    def get_cache(cache_name):
        if not CacheRepository.CACHES.has_key(cache_name):
            CacheRepository.CACHES[cache_name] = {}
        return CacheRepository.CACHES[cache_name]


class CacheMan(object):

    clearing = False

    def __init__(self, cache_name, expiration_minutes = 60):
        self.cache = CacheRepository.get_cache(cache_name)
        self.expiration_minutes = expiration_minutes
        today_str = datetime.date.today().strftime('%Y%m%d')
        if CacheRepository.DATE  != today_str:
            if CacheMan.clearing:
                pass
            else:
                CacheMan.clearing = True
                self.clear()
                CacheMan.clearing = False
            CacheRepository.DATE = datetime.date.today().strftime('%Y%m%d')

    def set_value(self, key, value, expiration_minutes = None):
        if expiration_minutes:
            mins = expiration_minutes
        else:
            mins = self.expiration_minutes
        expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        self.cache[key] = (expiration_time, value)
        return value

    def get_value(self, key):
        if self.cache.has_key(key):
            (expiration_time,value) = self.cache[key]
            if expiration_time > datetime.datetime.now():
                return value
            else:
                return None
        else:
            return None

    def clear(self):
        mutex = threading.Lock()
        mutex.acquire(1)
        for (k,v) in self.cache.iteritems():
            (expiration_time, value) = v
            if expiration_time < datetime.datetime.now():
                self.cache.pop(k)
        mutex.release()

    def get_with_cache(self, key, func_or_value, expiration_minutes=None):
        value = self.get_value(key)
        if value is None:
            if callable(func_or_value):
                assigned_value = func_or_value(key)
            else:
                assigned_value = func_or_value
            value = self.set_value(key, assigned_value, expiration_minutes)
        return value



if __name__ == '__main__':
    cache_man = CacheMan('option', expiration_minutes=0)
    print CacheMan('option').get_with_cache('spy', lambda x: x)

