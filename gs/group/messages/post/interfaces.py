# coding=utf-8
from zope.interface import Interface
from zope.schema import TextLine, ASCIILine, Field

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

