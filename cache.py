from time import sleep
from threading import Thread
import datetime
import threading

class Cache(threading.Thread):

    def __init__(self):
        self._courseCache = {}
        self.callback = self.clearCache
        self.event = threading.Event()
        self.time = 1800
        print("The current time of initialization is: " + str(datetime.datetime.now()))
        super(Cache, self).__init__()
    
    def run(self):
        while not self.event.wait(self.time):
            self.callback()

    def clearCache(self):
        print("The current time is: " + str(datetime.datetime.now()))
        print("Clearing Cache...")
        self._courseCache.clear()

    def add(self, key, cached_data):
        if key in self._courseCache:
            print("Cached item already exists.")
        else:
            self._courseCache[key] = cached_data
    
    def get(self, key):
        return self._courseCache[key] or None

    def get_cache(self):
        return self._courseCache

