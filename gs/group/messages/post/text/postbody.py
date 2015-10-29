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
from re import compile as re_compile
from textwrap import TextWrapper
from zope.component import getUtility
from gs.cache import cache
from gs.group.privacy import get_visibility, PERM_ANN
from gs.group.list.email.html.htmlbody import HTMLBody
from gs.group.list.email.html.matcher import (boldMatcher, emailMatcher, wwwMatcher, uriMatcher)
from .interfaces import IWrapEmail  # , IMarkupEmail
from .matcher import (youTubeMatcher, vimeoMatcher, publicEmailMatcher)
from .splitmessage import (split_message, SplitMessage, )

# this is currently the hard limit on the number of word's we will process.
# after this we insert a message. TODO: make this more flexible by using
# AJAX to incrementally fetch large emails
EMAIL_WORD_LIMIT = 5000


# The following expression is based on the one inside the
# TextWrapper class, but without the breaking on '-'.
splitExp = re_compile(r'(\s+|(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')


class OnlineHTMLBody(HTMLBody):
    '''The HTML form of a plain-text email body.

:param str originalText: The original (plain) text
:param object contentProvider: The content provider that is rendering this mess'''

    def __init__(self, originalText, contentProvider):
        super(OnlineHTMLBody, self).__init__(originalText)

        self.matchers = [youTubeMatcher, vimeoMatcher, boldMatcher, wwwMatcher, uriMatcher]
        messages = contentProvider.groupInfo.groupObj.messages
        if get_visibility(messages) == PERM_ANN:  # The messages are visible to Anon

            self.matchers += [publicEmailMatcher, ]
        else:
            self.matchers += [emailMatcher, ]
        sorted(self.matchers, key=attrgetter('weight'))


def wrap_message(messageText, width=79):
    """Word-wrap the message

:param str messageText: The text to alter.
:param int width: The column-number which to wrap at.
:returns: The wrapped text.
:rtype: str

.. Note: Originally a stand-alone script in
         ``Presentation/Tofu/MailingListManager/lscripts``."""
    email_wrapper = TextWrapper(
        width=width, expand_tabs=False, replace_whitespace=False, break_on_hyphens=False,
        break_long_words=False)
    email_wrapper.wordsep_re = splitExp
    filledLines = [email_wrapper.fill(l) for l in messageText.split('\n')]
    retval = '\n'.join(filledLines)
    return retval


def get_mail_body(contentProvider, text):
    """Get the body of the mail message, formatted for the Web.

:param object contentProvider: The content provider that is rendering the message.
:param str text: The text to extract a body from.
:returns: The formatted body of the email message.
:rtype: str

The ``self.post`` instance contains the plain-text version of the message, as was sent out to the
user's via email. For formatting on the Web it is necessary to convert the text to the correct
content-type, replace all URLs with anchor-elements, remove all at signs, wrap the message to 80
characters, and remove the file-notification. This method does these things."""
    retval = ''
    if text:
        wrapEmail = getUtility(IWrapEmail)
        text = wrapEmail(text)
        retval = text
    return retval


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
    mailBody = get_mail_body(contentProvider, text)
    plain = split_message(mailBody)

    markedUpIntro = ''
    if plain.intro:
        markedUpIntro = unicode(OnlineHTMLBody(plain.intro, contentProvider))

    markedUpRemainder = ''
    if plain.remainder:
        markedUpRemainder = unicode(OnlineHTMLBody(plain.remainder, contentProvider))

    retval = SplitMessage(markedUpIntro, markedUpRemainder)
    return retval
