# coding=utf-8
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider
from Products.XWFCore.XWFUtils import getOption
from postbody import get_post_intro_and_remainder
from queries import PostQuery

class GSPostContentProvider(GroupContentProvider):
    def __init__(self, context, request, view):
        GroupContentProvider.__init__(self, context, request, view)
        self.__updated = False

    def update(self):
        # See the interface for what is passed in.
        self.__updated = True
          
        self.authored = self.user_authored()
        self.authorInfo = createObject('groupserver.UserFromId',
                            self.context, self.post['author_id'])

        ir = get_post_intro_and_remainder(self.context, self.post['body'])
        self.postIntro, self.postRemainder = ir
        self.cssClass = self.get_cssClass()              
        
        self.hiddenPostDetails = None
        if self.post['hidden']:
            self.hiddenPostInfo = HiddenPostInfo(self.context, 
                                    self.post['post_id'])

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
            
        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        self.request.debug = False
        r = pageTemplate(self)
        return r

    #########################################
    # Non-standard methods below this point #
    #########################################

    def get_cssClass(self):
        assert hasattr(self, 'position') # passed in
        if ((self.position % 2) == 0):
            retval = 'even'
        else:
            retval = 'odd'
        assert retval in ('odd', 'even')
        return retval

    def user_authored(self):
        """Did the user write the email message?
          
          ARGUMENTS
              None.
          
          RETURNS
              A boolean that is "True" if the current user authored the
              email message, "False" otherwise.
              
          SIDE EFFECTS
              None.
              
        """
        user = self.request.AUTHENTICATED_USER
        retval = False
        if user.getId():
            retval = user.getId() == self.post['author_id']
        assert type(retval) == bool
        return retval

class HiddenPostInfo(object):
    def __init__(self, context, postId):
        self.postId = postId
        
        da = context.zsqlalchemy
        q = PostQuery(context, da)
        
        hiddenPostDetails = q.get_hidden_post_details(postId)
        m = 'No details for the hidden post %s' % postId
        assert hiddenPostDetails, m

        self.adminInfo = createObject('groupserver.UserFromId',
                            context, hiddenPostDetails['hiding_user'])

        self.date = hiddenPostDetails['date_hidden']
        self.reason = hiddenPostDetails['reason']

