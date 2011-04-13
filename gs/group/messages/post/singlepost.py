# coding=utf-8
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Unauthorized
from zope.cachedescriptors.property import Lazy
from Products.XWFMailingListManager.queries import MessageQuery
from Products.GSGroup.utils import is_public
from gs.group.base.page import GroupPage
from error import NoIDError, Hidden

class GSPostView(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.postId = self.request.get('postId', None)
        if not self.postId:
            raise NoIDError('No ID Specified')
    
    @Lazy
    def isPublic(self):
        assert self.groupInfo.groupObj, 'No group in the groupInfo!'
        retval = is_public(self.groupInfo.groupObj)
        assert type(retval) == bool
        return retval

    @Lazy
    def messageQuery(self):
        assert self.context, 'No context for a post!'
        da = self.context.zsqlalchemy 
        assert da, 'No data-adaptor found'
        retval = MessageQuery(self.context, da)
        assert retval
        return retval

    @Lazy
    def post(self):
        retval = self.messageQuery.post(self.postId)
        if not retval:
          raise NotFound(self, self.postId, self.request)
        if retval['group_id'] != self.groupInfo.id:
            m = u'You are not authorized to access this post from '\
                'the group %s' % self.groupInfo.name
            raise Unauthorized(m)
        if retval['hidden']:
            raise Hidden('The post %s is hidden' % self.postId)
        assert retval
        return retval
        
    @Lazy
    def relatedPosts(self):
        retval = self.messageQuery.topic_post_navigation(self.postId)
        return retval

    @Lazy
    def topicTitle(self):
        retval = self.post.get('subject', '')
        return retval

