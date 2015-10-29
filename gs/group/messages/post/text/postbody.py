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
from cgi import escape as cgi_escape
from re import compile as re_compile, I as re_I, M as re_M, U as re_U
from textwrap import TextWrapper
from zope.component import getUtility
from gs.cache import cache
from gs.group.privacy import get_visibility, PERM_ANN
from gs.group.list.email.html.htmlbody import HTMLBody
from .interfaces import IWrapEmail  # , IMarkupEmail
from .splitmessage import (split_message, SplitMessage, )

# this is currently the hard limit on the number of word's we will process.
# after this we insert a message. TODO: make this more flexible by using
# AJAX to incrementally fetch large emails
EMAIL_WORD_LIMIT = 5000

email_matcher = re_compile(r".*?([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,4}).*?",
                           re_I | re_M | re_U)
youtube_matcher = re_compile(
    "<?(?:https?:\/\/)?(?:www\.)?youtu(?:be)?\.(?:[a-z]){2,3}(?:[a-z/?=]+)"
    "([a-zA-Z0-9-_]{11})(?:\?[a-z0-9&-_=]+)?>?")
splashcast_matcher = re_compile("(?i)(http://www.splashcastmedia.com/"
                                "web_watch/\?code\=)(.*)($|\s)")
vimeo_matcher = re_compile(
    "(?i)(?:https?:\/\/)(?:.*)vimeo.com\/(.*)(?:$|\s)")

# The following expression is based on the one inside the
# TextWrapper class, but without the breaking on '-'.
splitExp = re_compile(r'(\s+|(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')


def escape_word(word):
    word = cgi_escape(word)
    return word


def markup_email_address(contentProvider, word, substituted, substituted_words):
    '''Markup an email address.

Some people become upset if their email address is shown to the general public.
To people becoming upset the email address is redacted (obscured) if, and only
if, Anonymous can view the message. In all other cases the email address is
shown.'''
    retval = word
    if not(substituted) and email_matcher.match(word):
        messages = contentProvider.groupInfo.groupObj.messages
        if get_visibility(messages) == PERM_ANN:
            # The messages in the group are visibile to the anonymous user,
            #   so obfuscate (redact) any email addresses in the post.
            retval = email_matcher.sub('&lt;email obscured&gt;', word)
        else:
            # The messages in the group are visibile to group members only
            # so show email addresses in the post, and make them useful.
            retval = '<a class="email" href="mailto:%s">%s</a>' % (word, word)

    assert retval, 'Email address <%s> not marked up' % word
    return retval


def markup_youtube(contentProvider, word, substituted, substituted_words):
    """ Markup youtube URIs.

    """
    if substituted:
        return word

    if word in substituted_words:
        return word

    word = youtube_matcher.sub(
        '\n<iframe width="462" height="260" '
        'src="https://www.youtube.com/embed/\g<1>" frameborder="0" '
        'allowfullscreen="allowfullscreen"></iframe>\n', word)
    return word


def markup_vimeo(contentProvider, word, substituted, substituted_words):
    """ Markup vimeo URIs.

    """
    if substituted:
        return word

    if word in substituted_words:
        return word

    word = vimeo_matcher.sub(
        '\n<iframe src="https://player.vimeo.com/video/\g<1>?'
        'color=ffffff&title=0&byline=0&badge=0" width="462" height="260" '
        'frameborder="0" allowfullscreen="allowfullscreen"></iframe>\n', word)

    return word


def markup_splashcast(contentProvider, word, substituted, substituted_words):
    """ Markup splashcast URIs.

    """
    if substituted:
        return word

    if word in substituted_words:
        return word

    word = splashcast_matcher.sub(
        '<div class="markup-splashcast"><embed '
        'src="http://web.splashcast.net/go/skin/\g<2>'
        '/sz/wide" wmode="Transparent" width="380" height="416" '
        'allowFullScreen="true" '
        'type="application/x-shockwave-flash" /></div>\g<3>', word)
    return word


def wrap_message(messageText, width=79):
    """Word-wrap the message

    ARGUMENTS
        "messageText" The text to alter.
        "width"       The column-number which to wrap at.

    RETURNS
        A string containing the wrapped text.

    SIDE EFFECTS
        None.

    NOTE
        Originally a stand-alone script in
        "Presentation/Tofu/MailingListManager/lscripts".

    """
    email_wrapper = TextWrapper(
        width=width, expand_tabs=False, replace_whitespace=False, break_on_hyphens=False,
        break_long_words=False)
    email_wrapper.wordsep_re = splitExp
    filledLines = [email_wrapper.fill(l) for l in messageText.split('\n')]
    retval = '\n'.join(filledLines)
    return retval


def get_mail_body(contentProvider, text):
    """Get the body of the mail message, formatted for the Web.

    The "self.post" instance contains the plain-text version
    of the message, as was sent out to the user's via email.
    For formatting on the Web it is necessary to convert the
    text to the correct content-type, replace all URLs with
    anchor-elements, remove all at signs, wrap the message to
    80 characters, and remove the file-notification. This method
    does these things.

    ARGUMENTS
        contentProvider:  The contentProvider of the message.
        text:     The text to extract a body from

    RETURNS
        A string representing the formatted body of the email
        message.

    SIDE EFFECTS
        None.
    """
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

    ARGUMENTS
        contentProvider:  The contentProvider for the post, providing
                  access to the context, groupInfo and other useful tidbits.
        text:     The text to split into an introduction and remainder

    RETURNS
        A 2-tuple of the strings that represent the email intro
        and the remainder.

    SIDE EFFECTS
        None.
    """
    if not contentProvider.groupInfo.groupObj:
        raise ValueError("The groupInfo object should always have a groupObj")
    mailBody = get_mail_body(contentProvider, text)
    plain = split_message(mailBody)
    markedUpIntro = unicode(HTMLBody(plain.intro)) if plain.intro else ''
    markedUpRemainder = unicode(HTMLBody(plain.remainder)) if plain.remainder else ''
    retval = SplitMessage(markedUpIntro, markedUpRemainder)
    return retval
