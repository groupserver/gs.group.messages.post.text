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
from re import compile as re_compile, I as re_I, M as re_M, U as re_U
from cgi import escape as cgi_escape
from textwrap import TextWrapper
from zope.component import getUtility
from gs.cache import cache
from gs.group.privacy import get_visibility, PERM_ANN
from .interfaces import IMarkupEmail, IWrapEmail

# this is currently the hard limit on the number of word's we will process.
# after this we insert a message. TODO: make this more flexible by using
# AJAX to incrementally fetch large emails
EMAIL_WORD_LIMIT = 5000

email_matcher = re_compile(r".*?([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,4}).*?",
                           re_I | re_M | re_U)
uri_matcher = re_compile("(?i)(http://|https://)(.+?)(\&lt;|\&gt;"
                         "|\)|\]|\}|\"|\'|$|\s)")
www_matcher = re_compile("""(?i)(www\..+)""")
youtube_matcher = re_compile(
    "<?(?:https?:\/\/)?(?:www\.)?youtu(?:be)?\.(?:[a-z]){2,3}(?:[a-z/?=]+)"
    "([a-zA-Z0-9-_]{11})(?:\?[a-z0-9&-_=]+)?>?")
splashcast_matcher = re_compile("(?i)(http://www.splashcastmedia.com/"
                                "web_watch/\?code\=)(.*)($|\s)")
vimeo_matcher = re_compile(
    "(?i)(?:https?:\/\/)(?:.*)vimeo.com\/(.*)(?:$|\s)")
bold_matcher = re_compile("""(\*.*\*)""")

# The following expression is based on the one inside the
# TextWrapper class, but without the breaking on '-'.
splitExp = re_compile(r'(\s+|(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')


def escape_word(word):
    word = cgi_escape(word)
    return word


def markup_uri(contentProvider, word, substituted, substituted_words):
    """ Markup URI in word.

    """
    if substituted:
        return word

    word = uri_matcher.sub('<a href="\g<1>\g<2>">\g<1>\g<2></a>\g<3>',
                           word)
    return word


def markup_www(contentProvider, word, substituted, substituted_words):
    """ Markup URIs starting with www, but no method.

    """
    if substituted:
        return word

    word = www_matcher.sub('<a href="http://\g<1>">\g<1></a>',
                           word)
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


def markup_bold(contentProvider, word, substituted, substituted_words):
    """Markup words that should be bold, because they have astersisks
      around them.
    """
    if substituted:
        # Do not substitute if the word has already been marked-up
        return word

    word = bold_matcher.sub('<b>\g<1></b>',
                            word)
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


def split_message(messageText, max_consecutive_comment=12,
                  max_consecutive_whitespace=3):
    """Split the message into main body and the footer.

    Email messages often contain a footer at the bottom, which
    identifies the user, and who they work for. However, GroupServer
    has lovely profiles which do this, so normally we want to snip
    the footer, to reduce clutter.

    In addition, many users only write a short piece of text at the
    top of the email, while the remainder of the message consists
    of all the previous posts. This method also removes the
    "bottom quoting".

    ARGUMENTS
        "messageText" The text to process.
        "max_consecutive_comment"    The maximum number of lines
            of quoting to allow before snipping.
        "max_consecutive_whitespace" The maximum number of lines
            that just contain whitespace to allow before snipping.

    RETURNS
        2-tuple, containing the strings representing the main-body
        of the message, and the footer.

    SIDE EFFECTS
        None.

    NOTE
        Originally a stand-alone script in
        "Presentation/Tofu/MailingListManager/lscripts".
    """
    slines = messageText.split('\n')

    intro = []
    body = []
    i = 1
    bodystart = False
    consecutive_comment = 0
    consecutive_whitespace = 0

    for line in slines:
        if ((line[:2] == '--') or (line[:2] == '==')
                or (line[:2] == '__') or (line[:2] == '~~')
                or (line[:3] == '- -')):
            bodystart = True

        # if we've started on the body, just append to body
        if bodystart:
            body.append(line)
        # count comments, but don't penalise top quoting as badly
        elif consecutive_comment >= max_consecutive_comment and i > 25:
            body.append(line)
            bodystart = True
        # if we've got less than 15 lines, just put it in the intro
        elif (i <= 15):
            intro.append(line)
        elif (len(line) > 3 and line[:4] != '&gt;'):
            intro.append(line)
        elif consecutive_whitespace <= max_consecutive_whitespace:
            intro.append(line)
        else:
            body.append(line)
            bodystart = True

        if len(line) > 3 and (line[:4] == '&gt;' or line.lower().find('wrote:') != -1):
            consecutive_comment += 1
        else:
            consecutive_comment = 0

        if len(line.strip()):
            consecutive_whitespace = 0
        else:
            consecutive_whitespace += 1

        i += 1

    # Backtrack through the post, in reverse order
    rintro = []
    trim = True

    for line in intro[::-1]:
        prevLine = intro.index(line) == 0 and '' or intro[intro.index(line) - 1]
        if len(intro) < 5:
            trim = False
        if len(line) > 3:
            ls = line[:4]
        elif line.strip():
            ls = line.strip()[0]
        else:
            ls = ''
        if trim and (ls == '&gt;' or ls == ''):
            body.insert(0, line)
        elif trim and line.find('wrote:') > 2:
            body.insert(0, line)
        elif ((trim) and (len(line.strip()) > 0)
              and (len(line.strip().split()) == 1)
              and ((len(prevLine.strip()) == 0)
              or len(prevLine.strip().split()) == 1)):
            # IF we are trimming, and the line has non-whitepsace
            #   characters AND there is only one word on the line,
            #   AND the previous line does NOT have any significant text
            # THEN add it to the snipped-text.
            body.insert(0, line)
        else:
            trim = False
            rintro.insert(0, line)

    # Do not snip, if we will only snip a single line of
    #  actual content
    if(len(body) == 1):
        rintro = rintro + body
        body = []

    intro = '\n'.join(rintro)
    body = '\n'.join(body)
    retval = (intro.strip(), body)
    assert retval
    assert len(retval) == 2
    return retval

standard_markup_functions = (markup_email_address, markup_youtube,
                             markup_splashcast, markup_vimeo,
                             markup_uri, markup_www, markup_bold)


def markup_word(contentProvider, word, substituted_words):
    word = escape_word(word)
    substituted = False

    for function in standard_markup_functions:
        nword = function(contentProvider, word, substituted, substituted_words)
        if nword != word:
            substituted = True
            if word not in substituted_words:
                substituted_words.append(word)
        word = nword
    return word


def markup_email(contentProvider, text):
    retval = ''
    substituted_words = []
    word_count = 0

    if text:
        out_text = ''
        curr_word = ''
        for char in text:
            if char.isspace():
                if curr_word:
                    markedUpWord = markup_word(contentProvider, curr_word,
                                               substituted_words)
                    curr_word = ''
                    out_text += markedUpWord
                    word_count += 1
                    if word_count > EMAIL_WORD_LIMIT:
                        out_text += '\n\n<strong>This email has been '\
                            'automatically truncated to 5000 words.</strong>'
                        break
                out_text += char
            else:
                curr_word += char
        if curr_word:
            markedUpWord = markup_word(contentProvider, curr_word,
                                       substituted_words)
            out_text += markedUpWord
        retval = out_text.strip()
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

        markupEmail = getUtility(IMarkupEmail)
        text = markupEmail(contentProvider, text)

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
    retval = split_message(mailBody)
    return retval
