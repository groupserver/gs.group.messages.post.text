# coding=utf-8
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from Products.XWFMailinListManager.queries import MessageQuery
from gs.group.base.page import GroupPage

class GSPostTraversal(GroupPage):
    implements(IPublishTraverse)
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.__messageQuery = None

    @property
    def messageQuery(self):
        assert self.context
        if self.__messageQuery == None:
            da = self.context.zsqlalchemy 
            assert da, 'No data-adaptor found'
            self.__messageQuery = MessageQuery(self.context, da)
        return self.__messageQuery
        
    def publishTraverse(self, request, name):
        if not request.has_key('postId'):
            self.request['postId'] = name
        return self
    
    def __call__(self):
        return getMultiAdapter((self.context, self.request), name="gspost")()

