# coding=utf-8
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider
from Products.XWFCore.cache import LRUCache, SimpleCache
from Products.XWFCore.XWFUtils import getOption
from Products.XWFMailingListManager.emailbody import get_email_intro_and_remainder

class GSPostContentProvider(GroupContentProvider):
    # We want a really simple cache for templates, because there aren't
    # many of them
    cookedTemplates = SimpleCache("GSPostContentProvider.cookedTemplates")
      
    # Setup a least recently used expiry cache for results
    cookedResult = LRUCache("GSPostContentProvider.cookedResult")
    cookedResult.set_max_objects(1024)
      
    post = None
    def __init__(self, context, request, view):
        GroupContentProvider.__init__(self, context, request, view)
        self.__updated = False

    def update(self):
        """Update the internal state of the post content-provider.
          
        This method can be considered the main "setter" for the 
        content provider; for the most part, information about the post's 
        author is set.
        
        SIDE EFFECTS
          The following attributes are set.
            * "self.__updated"     Set to "True"
            * "self.authorId"      Set to the user-id of the post author.
            * "self.authorName"    Set to the name of the post author.
            * "self.authorExists"  Set to "True" if the author exists
            * "self.authored"      Set to "True" if the current user 
                                   authored the post.
            * "self.authorImage"   Set to the URL of the author's image.
            * "self.siteInfo"     Set to an instance of GSSiteInfo
            * "self.groupInfo"    Set to an instance of GSGroupInfo
        """
        assert self.post
        
        self.__updated = True
        
        # setup a cache key based on the unique attributes of this post
        tz = getOption(self.context, 'tz', default='UTC')
        self.cacheKey = '%s:%s:%s:%s:%s' % (self.post['post_id'], 
            self.position, self.topicName, self.pageTemplateFileName,
            tz)
          
        if not self.cookedResult.has_key(self.cacheKey):
            self.authored = self.user_authored()
            self.authorInfo = self.get_author()
            ir = get_email_intro_and_remainder(self.context,
                                               self.post['body'])
            self.postIntro, self.postRemainder = ir
            self.cssClass = self.get_cssClass()              
            self.filesMetadata = self.post['files_metadata']
          
    def render(self):
        """Render the post
          
        The donkey-work of this method is done by "self.pageTemplate", 
        which is set when the content-provider is created.
          
        RETURNS
            An HTML-snippet that represents the post.
            
        """
        if not self.__updated:
            raise UpdateNotCalled
              
        r = self.cookedResult.get(self.cacheKey)
        if not r:
            pageTemplate = self.cookedTemplates.get(self.pageTemplateFileName)
            if not pageTemplate:
                pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)    
                self.cookedTemplates.add(self.pageTemplateFileName, pageTemplate)
              
            self.request.debug = False
            r = pageTemplate(self, 
                             authorInfo=self.authorInfo,
                             authored=self.authored, 
                             showPhoto=self.showPhoto, 
                             postIntro=self.postIntro,
                             postRemainder=self.postRemainder, 
                             cssClass=self.cssClass, 
                             topicName=self.topicName, 
                             filesMetadata=self.filesMetadata,
                                post=self.post, 
                                context=self.context, 
                                siteName = self.siteInfo.get_name(), 
                                siteURL = self.siteInfo.get_url(), 
                                groupId = self.groupInfo.get_id(),
                                isPublic = self.isPublic)
            self.cookedResult.add(self.cacheKey, r)
          
        return r

    #########################################
    # Non-standard methods below this point #
    #########################################

    def get_cssClass(self):
        retval = ''
        even = (self.position % 2) == 0
        if even:
            retval = 'even'
        else:
            retval = 'odd'
                  
        assert retval
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
                    
        assert retval in (True, False)
        return retval

    def get_author(self):
        """ Get the user object associated with the author.
          
          RETURNS
             The user object if the author has an account, otherwise None.
          
        """
        authorId = self.post['author_id']
        author_cache = getattr(self.view, '__author_object_cache', {})
        user = author_cache.get(authorId, None)
        if not user:
            user = createObject('groupserver.UserFromId',
                self.context, self.post['author_id'])
            author_cache[authorId] = user
            self.view.__author_object_cache = author_cache
              
        return user

