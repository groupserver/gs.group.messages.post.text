# coding=utf-8
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider
from Products.XWFCore.XWFUtils import getOption
from Products.XWFCore.cache import SimpleCache
from postbody import get_post_intro_and_remainder
from hiddendetails import HiddenPostInfo

class GSPostContentProvider(GroupContentProvider):
    # We maintain a really simple cache for the actual page templates which
    # are read from disk. This avoids the overhead of reading and parsing
    # the template for every post.
    cookedTemplates = SimpleCache("GSPostContentProvider.cookedTemplates")
    
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

    def render(self):
        """Render the post
          
        The donkey-work of this method is done by "self.pageTemplate", 
        which is set when the content-provider is created.
          
        RETURNS
            An HTML-snippet that represents the post.
            
        """
        if not self.__updated:
            raise UpdateNotCalled
    
        pageTemplate = self.cookedTemplates.get(self.pageTemplateFileName)
        if not pageTemplate:
	    pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
            self.cookedTemplates.add(self.pageTemplateFileName,
                                     pageTemplate)
        
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

        assert isinstance(retval, bool)

        return retval

