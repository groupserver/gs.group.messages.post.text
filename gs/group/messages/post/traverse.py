# coding=utf-8
from zope.component import getMultiAdapter
from zope.location.interfaces import LocationError
from gs.group.base.page import GroupPage

class GSPostTraversal(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.__messageQuery = None
        
    def publishTraverse(self, request, name):
        if not request.has_key('postId'):
            self.request['postId'] = name
        return self
    
    def __call__(self):
        try:
            retval = getMultiAdapter((self.context, self.request), name="gspost")()
        except LocationError, e:
            retval = 'Ooops, Location error %s' % e
        except AssertionError, e:
            retval = 'Ooops, Assertion error %s' % e
        except KeyError, e:
            retval = 'Ooops, Key error %s' % e
        except ValueError, e:
            retval = 'Ooops, Value error %s' % e
        return retval

