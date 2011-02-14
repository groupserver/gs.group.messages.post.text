# coding=utf-8
from zope.interface import Interface
from zope.schema import TextLine, ASCIILine, Field, Int, Bool

class INavLinksContentProvider(Interface):
    topicTitle = TextLine(title=u"Title of the Topic",
        description=u'The title of the topic.',
        required=True)
                     
    relatedPosts = Field(title=u'Related Posts',
        description=u'The posts in the same topic.',
        required=True)

    pageTemplateFileName = ASCIILine(title=u"Page Template File Name",
        description=u"""The name of the ZPT file
        that is used to render the post.""",
        required=False,
        default='browser/templates/navlinks.pt')

class IGSPostContentProvider(Interface):
    """The Groupserver Post Content Provider Interface
      
      This interface defines the fields that must be set up, normally using
      TAL, before creating a "GSPostContentProvider" instance. See the
      latter for an example."""
    post = Field(title=u"Email Message Instance",
        description=u"The email instance to display",
        required=True, 
        readonly=False)
    position = Int(title=u"Position of the Post",
        description=u"""The position of the post in the topic.
        This is mostly used for determining the background 
        colour of the post.""",
        required=False,
        min=1, default=1)
    topicName = TextLine(title=u"Title of the Topic",
        description=u"""The title of the topic.""",
        required=False,
        default=u'')
    # Should really be called "same author" or similar.
    showPhoto = Bool(title=u'Whether to show the photo',
        description=u"""Determines if the author's photo
        should be shown.""",
        required=False,
        default=True)

    isPublic = Bool(title=u"Is the group public?",
        description=u"""Whether or not the group in which this post is
          displayed is public""",
        required=True)
    
    pageTemplateFileName = ASCIILine(title=u"Page Template File Name",
        description=u'The name of the ZPT file that is used to render '\
            u'the post.',
        required=False,
        default="browser/templates/postcontentprovider.pt")

