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
from __future__ import absolute_import, unicode_literals, print_function
from operator import attrgetter
from gs.cache import cache
from gs.group.privacy import get_visibility, PERM_ANN
from gs.group.messages.text import (
    split_message, SplitMessage, HTMLBody, boldMatcher, emailMatcher, wwwMatcher, uriMatcher,
    wrap_message)
from Products.GSGroup.interfaces import IGSMailingListInfo
from .matcher import (youTubeMatcher, vimeoMatcher, PublicEmailMatcher, )

# this is currently the hard limit on the number of word's we will process.
# after this we insert a message. TODO: make this more flexible by using
# AJAX to incrementally fetch large emails
EMAIL_WORD_LIMIT = 5000


class OnlineHTMLBody(HTMLBody):
    '''The HTML form of a plain-text email body.

:param str originalText: The original (plain) text
:param object contentProvider: The content provider that is rendering this mess'''

    def __init__(self, originalText, perm, okAddresses):
        super(OnlineHTMLBody, self).__init__(originalText)

        self.matchers = [youTubeMatcher, vimeoMatcher, boldMatcher, wwwMatcher, uriMatcher]
        if perm == PERM_ANN:  # The messages are visible to Anon
            p = PublicEmailMatcher(okAddresses)
            self.matchers.append(p)
        else:
            self.matchers.append(emailMatcher)
        sorted(self.matchers, key=attrgetter('weight'))


@cache('gs.group.messages.post.postintroremainder',
       lambda contentProvider, text: ':'.join(
           (str(contentProvider.post['post_id']),
            str((get_visibility(contentProvider.groupInfo.groupObj))))
       ), 3600)
def get_post_intro_and_remainder(contentProvider, text):
    """Get the introduction and remainder text of the formatted post

:param object contentProvider: The content provider renderning the message, providing access to
                               the context, groupInfo and other useful tidbits.
:parm str text: The text to split into an introduction and remainder
:returns:  A 2-tuple of the strings that represent the email intro and the remainder."""
    if not contentProvider.groupInfo.groupObj:
        raise ValueError("The groupInfo object should always have a groupObj")

    if not text:
        # Sorry, Dijkstra
        return SplitMessage('', '')
    mailBody = wrap_message(text)
    plain = split_message(mailBody)

    messages = contentProvider.groupInfo.groupObj.messages
    perm = get_visibility(messages)

    ml = IGSMailingListInfo(contentProvider.groupInfo.groupObj)
    okAddresses = (contentProvider.siteInfo.get_support_email(),
                   ml.get_property('mailto'))

    markedUpIntro = ''
    if plain.intro:
        markedUpIntro = unicode(OnlineHTMLBody(plain.intro, perm, okAddresses))

    markedUpRemainder = ''
    if plain.remainder:
        markedUpRemainder = unicode(OnlineHTMLBody(plain.remainder, perm, okAddresses))

    retval = SplitMessage(markedUpIntro, markedUpRemainder)
    return retval
