# coding=utf-8
from urllib import quote
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider
from Products.XWFCore.XWFUtils import getOption
from postbody import get_post_intro_and_remainder
from hiddendetails import HiddenPostInfo
from canhide import can_hide_post
from gs.cache import cache
from threading import RLock

class GSPostContentProvider(GroupContentProvider):
    post = None
    __thread_lock = RLock()
    cookedTemplates = {}
    def __init__(self, context, request, view):
        GroupContentProvider.__init__(self, context, request, view)
        self.__updated = False
        # allow baseclass override
        self.can_hide_post = can_hide_post

    def update(self):
        """Update the internal state of the post content-provider.
          
        This method can be considered the main "setter" for the 
        content provider; for the most part, information about the post's 
        author is set.
        
        SIDE EFFECTS
          The following attributes are set.
            * "self.__updated"     Set to "True".
            * "self.authorId"      Set to the user-id of the post author.
            * "self.authorName"    Set to the name of the post author.
            * "self.authorExists"  Set to "True" if the author exists.
            * "self.authored"      Set to "True" if the current user 
                                   authored the post.
            * "self.authorImage"   Set to the URL of the author's image.
            * "self.siteInfo"     Set to an instance of GSSiteInfo.
            * "self.groupInfo"    Set to an instance of GSGroupInfo.
            * "self.post"         Set to the content of the post.
        """
        assert self.post
        # See the interface for what is passed in.
        self.__updated = True
        
        self.showPhoto = self.showPhoto and (not self.post['hidden'])
                  
        self.authored = self.user_authored()
        self.authorInfo = createObject('groupserver.UserFromId',
                            self.context, self.post['author_id'])

        ir = get_post_intro_and_remainder(self, self.post['body'])
        self.postIntro, self.postRemainder = ir
        self.cssClass = self.get_cssClass()              
    
        self.hiddenPostDetails = None
        if self.post['hidden']:
            self.hiddenPostInfo = HiddenPostInfo(self.context, 
                                    self.post['post_id'])
                                    
        self.canHide = self.can_hide_post(self.loggedInUser, self.groupInfo, 
                                        self.post)

    # @cache('GSPostContentProvider.cooked', lambda x,y: y, 3600)
    def cook_template(self, fname):
        if self.cookedTemplates.has_key(fname):
            return self.cookedTemplates[fname]

        cooked = ViewPageTemplateFile(fname)
        try:
            # don't block, we'll just cache it later
            if self.__thread_lock.acquire(False):
                self.cookedTemplates[fname] = cooked
        finally:
            self.__thread_lock.release()
        
        return cooked

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = self.cook_template(self.pageTemplateFileName)
        self.request.debug = False
        r = pageTemplate(self)
        return r

    #########################################
    # Non-standard methods below this point #
    #########################################

    def get_cssClass(self):
        assert hasattr(self, 'position') # passed in
        retval = (((self.position % 2) == 0) and 'even ') or 'odd '
        retval += self.post['hidden'] and 'hidden disclosureWidget' or \
          'visible'
        return retval

    def user_authored(self):
        retval = False
        if not(self.loggedInUser.anonymous):
            retval = self.loggedInUser.id == self.post['author_id']
        assert type(retval) == bool
        return retval
        
    def quote(self, msg):
        assert msg
        retval = quote(msg)
        assert retval
        return retval
        
    @Lazy
    def loggedInUser(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        assert retval
        return retval

