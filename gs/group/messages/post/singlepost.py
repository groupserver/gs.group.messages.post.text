# coding=utf-8
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Unauthorized
from Products.XWFMailingListManager.queries import MessageQuery
from Products.GSGroup.utils import is_public
from gs.group.base.page import GroupPage
from error import NoIDError

class GSPostView(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.__isPublic = self.__messageQuery = self.__post = \
            self.__relatedPosts = None
        self.postId = self.request.get('postId', None)
        if not self.postId:
            raise NoIDError('No ID Specified')
    
    @property
    def isPublic(self):
        if self.__isPublic == None:
            assert self.groupInfo.groupObj, 'No group in the groupInfo!'
            self.__isPublic = is_public(self.groupInfo.groupObj)
        return self.__isPublic

    @property
    def messageQuery(self):
        if self.__messageQuery == None:
            assert self.context, 'No context for a post!'
            da = self.context.zsqlalchemy 
            assert da, 'No data-adaptor found'
            self.__messageQuery = MessageQuery(self.context, da)
        assert self.__messageQuery
        return self.__messageQuery

    @property
    def post(self):
        if self.__post == None:
            self.__post = self.messageQuery.post(self.postId)
            if not self.__post:
              raise NotFound(self, self.postId, self.request)
            if self.__post['group_id'] != self.groupInfo.id:
                m = u'You are not authorized to access this post from '\
                    'the group %s' % self.groupInfo.name
                raise Unauthorized(m)
            # TODO: Check for a post being hidden. Hidden posts will 
            # sometimes raise a 410
            # <https://projects.iopen.net/groupserver/ticket/316>
        assert self.__post
        return self.__post
        
    @property
    def relatedPosts(self):
        if self.__relatedPosts == None:
            self.__relatedPosts = \
                self.messageQuery.topic_post_navigation(self.postId)
        return self.__relatedPosts

    @property
    def topicTitle(self):
        retval = self.post.get('subject', '')
        return retval

