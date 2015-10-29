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
from collections import (deque, namedtuple)
from re import (compile as re_compile, )

#: The 2-tuple containing the strings representing
#:
#: 0. The main body of the message (``intro``) and
#: 1. The rest of the message, including the bottom-quoting and the footer (``remainder``).
SplitMessage = namedtuple('SplitMessage', ['intro', 'remainder'])

#: The regular expression for the **title** **element** **contents.** For example,
#: ``Post by Dinsdale Piranha: Violence: British gangland: Ethel the Frog``. If we see this then
#: an email client, such as Mozilla Thunderbird, has decided to bottom quote, and convert the
#: contents of the ``<head>`` element to plain text. This would be fine if it was just the
#: ``<title>`` element, but it will be followed by some rather ugly CSS from some ``<style>``
#: elements.
#:
#: The four components seperated by a colon are the author-name, topic-name, group name, and
#: site name. *At least* three groups sperated by colons are expected, but there could be more if
#: any name contains a colon itself.
postByRE = re_compile('^\s*Post by (.*:){3,}')

#: The strings that are commonly used to explicitly indicate a signiture starting
EXPLICIT_SIG_START = ['--', '==', '~~', '__']


def split_message(messageText, max_consecutive_comment=12, max_consecutive_whitespace=3):
    """Split the message into main body and the footer.

:param str messageText: The text to process.
:param int max_consecutive_comment: The maximum number of lines of quoting to allow before snipping.
:param int max_consecutive_whitespace: The maximum number of lines that just contain whitespace to
    allow before snipping.
:returns: 2-tuple, containing the strings representing the main-body of the message, and the footer.
:rtype: :class:`SplitMessage`

Email messages often contain a footer at the bottom, which identifies the user, and who they work
for. However, GroupServer has lovely profiles which do this, so normally we want to snip the footer,
to reduce clutter.

In addition, many users only write a short piece of text at the top of the email, while the
remainder of the message consists of all the previous posts. This method also removes the
*bottom quoting*.

Originally a ZMI-side script in ``Presentation/Tofu/MailingListManager/lscripts``."""
    intro = []
    remainder = deque()
    remainder_start = False
    consecutive_comment = 0
    consecutive_whitespace = 0

    for i, line in enumerate(messageText.split('\n'), 1):
        if ((line[:2] in EXPLICIT_SIG_START) or (line[:3] == '- -') or postByRE.match(line)):
            remainder_start = True

        if remainder_start:
            # If we've started on the remainder, just append to the remainder
            remainder.append(line)
        elif (consecutive_comment > max_consecutive_comment) and (i > 25):
            # Add comments (quotes) to the remainder, but don't penalise top-quoting
            remainder.append(line)
            remainder_start = True
        elif (i <= 15):
            # if we've got less than 15 lines, just put it in the intro
            intro.append(line)
        elif (len(line) > 3) and ((line[:4] != '&gt;') or (line[:2] != '> ')):
            intro.append(line)
        elif consecutive_whitespace < max_consecutive_whitespace:
            # It is < (rather than <=) because of how we count the lines
            intro.append(line)
        else:
            remainder.append(line)
            remainder_start = True

        # Raise a flag if we see a quote (comment). This is used in the if-statement above
        if (len(line) > 3) and ((line[:4] == '&gt;') or (line[:2] == '> ')
                                or (line.lower().find('wrote:') != -1)):
            consecutive_comment += 1
        else:
            consecutive_comment = 0
        # Raise a flag if we see a whitespace. This is used in the major if-statement above
        if len(line.strip()):
            consecutive_whitespace = 0
        else:
            consecutive_whitespace += 1

    # Backtrack through the intro, in reverse order, adding things to either the remainder or
    # keeping them in the intro
    rintro = deque()
    trim = True
    for i, line in enumerate(intro[::-1]):
        if len(intro) < 5:
            trim = False

        if trim:
            ls = line[:4] if len(line) > 3 else ''
            if (((ls == '&gt;') or (ls[:2] == '> ') or (ls.strip() == '')
                 or (line.find('wrote:') > 2))):
                # IF we are trimming, and we are looking at a quote-character or an empty string
                #   OR we have seen the 'wrote:' marker
                # THEN add it to the snipped-text.
                remainder.appendleft(line)
            else:
                trim = False
                rintro.appendleft(line)
        else:
            rintro.appendleft(line)

    # Do not snip, if we will only snip a single line of actual content
    if (len(remainder) == 1) or ((len(remainder) == 2) and ('' in remainder)):
        rintro.extend(remainder)
        remainder = []

    intro = '\n'.join(rintro).strip()
    remainder = '\n'.join(remainder)

    # If we have snipped too much
    if not intro:
        intro = remainder
        remainder = ''

    retval = SplitMessage(intro, remainder)
    return retval
