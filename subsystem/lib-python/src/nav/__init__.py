"""
$Id$

This file is part of the NAV project.

Provides a common root package for the NAV python library.

Copyright (c) 2003 by NTNU, ITEA nettgruppen
Authors: Morten Vold <morten.vold@itea.ntnu.no>
"""
import time

class CachedObject:
    """
    A simple class to wrap objects for 'caching'.  It contains the
    object reference and the time the object was cached.
    """
    def __init__(self, object=None, loadTime=None):
        if not loadTime:
            loadTime = time.time()

        self.loadTime = loadTime
        self.object = object

    def age(self):
        """
        Return the age of this object
        """
        return time.time() - self.loadTime

    def __repr__(self):
        return "<%s cached at %s>" % (repr(self.object),
                                      time.asctime(time.localtime(self.loadTime)))
    
    def __str__(self):
        return self.object.__str__()

class ObjectCache(dict):
    def __setitem__(self, key, item):
        if not isinstance(item, CacheableObject):
            raise ValueError, "ObjectCache only caches CacheableObject instances, not %s" % type(item)
        else:
            if self.has_key(key):
                raise CacheError, "An object keyed %s is already stored in the cache" % repr(key)
            dict.__setitem__(self, key, item)
            item.cache = self

    def __delitem__(self, key):
        self[key].cache = None
        dict.__delitem__(self, key)

    def cache(self, object):
        """Caches the object, which must be a CacheableObject instance"""
        if not isinstance(object, CacheableObject):
            raise ValueError, "ObjectCache only caches CacheableObject instances, not %s" % type(object)
        else:
            self[object.key] = object

    def invalidate(self):
        """Removes all invalid objects from the cache, and returns the
        number of objects removed."""
        count = 0
        for key in self.keys():
            if self[key].isInvalid():
                del self[key]
                count += 1
        return count

    def refresh(self):
        """Refreshes all invalid objects in the cache, and returns the
        number of objects refreshed."""
        count = 0
        for key in self.keys():
            if self[key].isInvalid() and self[key].refresh():
                count += 1
        return count    

class CacheableObject:
    """
    A simple class to wrap objects for 'caching'.  It contains the
    object reference and the time the object was loaded.
    """
    def __init__(self, object=None):
        self.object = object
        self._cache = None
        self.cacheTime = None
        self.key = str(object)

    def __setattr__(self, name, item):
        if name == 'cache':
            if (self._cache is not None and item is not None):
                raise CacheError, "%s is already cached" % repr(self)
            elif item is not None:
                self._cache = item
                self.cacheTime = time.time()
            else:
                self._cache = None
                self.cacheTime = None
        else:
            try:
                dict.__setattr__(self, name, item)
            except:
                self.__dict__[name] = item

    def __getattr__(self, name):
        if name == 'cache':
            return self._cache
        else:
            raise AttributeError, name

    def isCached(self):
        return self._cache is not None

    def isInvalid(self):
        """Returns True if this object is too old (or invalid in some
        other way) to remain in the cache."""
        return False

    def refresh(self):
        """Refresh the object, if possible"""
        return False

    def invalidate(self):
        """Delete this object from the cache it is registered in."""
        if self.cache is not None and self.isInvalid():
            del self.cache[self.key]
            return True
        else:
            return False

    def age(self):
        """
        Return the cache age of this object.
        """
        if self.cacheTime is None:
            return 0
        else:
            return time.time() - self.cacheTime

    def __repr__(self):
        if self._cache is None:
            return "<%s uncached>" % repr(self.object)
        else:
            return "<%s cached at %s>" % (repr(self.object),
                                          time.asctime(time.localtime(self.cacheTime)))
    
    def __str__(self):
        return self.object.__str__()

class CacheError(Exception):
    pass

# We import some sub-modules because of bugs in mod_python
import db
import auth
try:
    # This actually belongs in another subsystem
    import web
except:
    pass

