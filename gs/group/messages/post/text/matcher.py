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
from gs.group.messages.text import Matcher

START = '</span><!--Line continues-->\n<br/>\n<iframe width="462" height="260" '
END = 'frameborder="0" allowfullscreen="allowfullscreen"></iframe><br/>\n'\
      '<span class="line line-continued">'

#: The :class:`Matcher` instance that turns URI links to YouTube into embedded
#: videos.
youTubeMatcher = Matcher(
    r"(?P<leading>\&lt;|\(|\[|\{|\"|\'|^)"
    r"(?P<protocol>http://|https://)"
    r"(?P<host>(www\.)?youtu(be)?\.([a-z]){2,3})"
    r"(?P<query>[a-z/?=]+)"
    r"(?P<videoId>[a-zA-Z0-9-_]{11})"  # This is the important part
    r"(?P<rest>\?[a-z0-9&-_=]+)?"
    r"(?P<trailing>\&gt;|\)|\]|\}|\"|\'|$|\s)",
    START + 'src="https://www.youtube.com/embed/\g<videoId>" ' + END, 25)

#: The :class:`Matcher` instance that turns URI links to Vimeo into embedded
#: videos.
vimeoMatcher = Matcher(
    r"(?P<leading>\&lt;|\(|\[|\{|\"|\'|^)"
    r"(?P<protocol>http://|https://)"
    r"(?P<host>.*vimeo.com)"
    r"(?P<videoId>.*)"  # This is the important part
    r"(?P<trailing>\&gt;|\)|\]|\}|\"|\'|$|\s)",
    START + 'src="https://player.vimeo.com/video\g<videoId>?color=ffffff&title=0&byline=0&badge=0"'
    + END, 26)


class PublicEmailMatcher(Matcher):
    def __init__(self, okAddresses=None):
        super(PublicEmailMatcher, self).__init__(
            r"(?P<leading>.*?)"
            r"(?P<address>[A-Z0-9\._%+-]+@[A-Z0-9.-]+\.[A-Z]+)"
            r"(?P<trailing>.*)",
            r'<span class="email">\g<leading>&lt;email obscured&gt;\g<trailing></span>', 20)
        self.okAddresses = [] if okAddresses is None else okAddresses

    def sub(self, s):
        m = self.re.match(s)
        gd = m.groupdict()
        if gd['address'] in self.okAddresses:
            r = '<a class="email" href="mailto:{address}">{leading}{address}{trailing}</a>'
            retval = r.format(address=gd['address'], leading=gd['leading'], trailing=gd['trailing'])
        else:
            retval = super(PublicEmailMatcher, self).sub(s)
        assert retval, 'There is no retval'
        return retval

#: The :class:`Matcher` instance that redacts email addresses for public groups.
publicEmailMatcher = PublicEmailMatcher()
