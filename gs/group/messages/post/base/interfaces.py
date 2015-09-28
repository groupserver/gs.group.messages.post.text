# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2012, 2013, 2014, 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from zope.interface import Interface
from zope.schema import TextLine, ASCIILine, Field, Int, Bool, Text
from gs.core import to_ascii
from . import GSMessageFactory as _


class INavLinksContentProvider(Interface):
    topicTitle = TextLine(
        title="Title of the Topic",
        description='The title of the topic.',
        required=True)

    relatedPosts = Field(
        title='Related Posts',
        description='The posts in the same topic.',
        required=True)

    pageTemplateFileName = ASCIILine(
        title="Page Template File Name",
        description="""The name of the ZPT file
        that is used to render the post.""",
        required=False,
        default=to_ascii('browser/templates/navlinks.pt'))


class IGSPostContentProvider(Interface):
    """The Groupserver Post Content Provider Interface

      This interface defines the fields that must be set up, normally using
      TAL, before creating a "GSPostContentProvider" instance. See the
      latter for an example."""
    post = Field(
        title="Email Message Instance",
        description="The email instance to display",
        required=True,
        readonly=False)
    position = Int(
        title="Position of the Post",
        description="""The position of the post in the topic.
        This is mostly used for determining the background
        colour of the post.""",
        required=False,
        min=1, default=1)
    topicName = TextLine(
        title="Title of the Topic",
        description="""The title of the topic.""",
        required=True,
        default='')
    # Should really be called "same author" or similar.
    showPhoto = Bool(
        title='Whether to show the photo',
        description="""Determines if the author's photo
        should be shown.""",
        required=False,
        default=True)

    isPublic = Bool(
        title="Is the group public?",
        description="""Whether or not the group in which this post is
          displayed is public""",
        required=True)

    showRemainder = Bool(
        title='Show the remainder',
        description='True if the bottom-quoting should be shown',
        required=False,
        default=False)

    pageTemplateFileName = ASCIILine(
        title="Page Template File Name",
        description='The name of the ZPT file that is used to render '
                    'the post.',
        required=False,
        default=to_ascii("browser/templates/postcontentprovider.pt"))

# Used for some utilities


class IMarkupEmail(Interface):
    pass


class IWrapEmail(Interface):
    pass


class IHide(Interface):
    postId = TextLine(
        title='Post Identifier',
        description='The identifier of the post that is to be hidden',
        required=True)

    reason = Text(
        title=_('hide-reason', 'Reason'),
        description=_('hide-reason-help',
                      'The reason the post needs to be hidden.'),
        required=True)
