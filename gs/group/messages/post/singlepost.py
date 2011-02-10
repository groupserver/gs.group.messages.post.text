# coding=utf-8
from zope.security.interfaces import Unauthorized
from Products.XWFMailingListManager.queries import MessageQuery
from Products.GSGroup.utils import is_public
from gs.group.base.page import GroupPage

class GSPostView(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.__isPublic = self.__messageQuery = self.__post = \
            self.__relatedPosts = None
        self.postId = self.request['postId']
    
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
        return self.__messageQuery

    @property
    def post(self):
        if self.__post == None:
            self.__post = self.messageQuery.post(self.postId)
            assert self.__post # TODO: Raise something: Not found error
            if self.__post['group_id'] != self.groupInfo.id:
                m = u'You are not authorized to access this post from '\
                    'the group %s' % self.groupInfo.name
                raise Unauthorized(m)
        return self.__post
        
    @property
    def relatedPosts(self):
        if self.__relatedPosts == None:
            self.__relatedPosts = \
                self.messageQuery.topic_post_navigation(self.postId)
        return self.__relatedPosts

    def do_error_redirect(self):
        if not self.postId:
            self.request.response.redirect('/r/post-no-id')
        else:
            self.request.response.redirect('/r/post-not-found?id=%s' % self.postId)
          
    def get_topic_title(self):
        assert hasattr(self, 'post')
        retval = self.post and self.post['subject'] or ''
        return retval
          
    def get_previous_post(self):
        assert hasattr(self, 'relatedPosts')
        assert self.relatedPosts.has_key('previous_post_id')
        return self.relatedPosts['previous_post_id']
                    
    def get_next_post(self):
        assert hasattr(self, 'relatedPosts')
        assert self.relatedPosts.has_key('next_post_id')
        return self.relatedPosts['next_post_id']
          
    def get_first_post(self):
        assert hasattr(self, 'relatedPosts')
        assert self.relatedPosts.has_key('first_post_id')
        return self.relatedPosts['first_post_id']
          
    def get_last_post(self):
        assert hasattr(self, 'relatedPosts')
        assert self.relatedPosts.has_key('last_post_id')
        return self.relatedPosts['last_post_id']
          
    def get_post(self):
        assert hasattr(self, 'post')
        return self.post

