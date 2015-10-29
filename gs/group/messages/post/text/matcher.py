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
from gs.group.list.email.html.matcher import Matcher


youTubeMatcher = Matcher(
    r"(?P<leading>\&lt;|\(|\[|\{|\"|\'|^)"
    r"(?P<protocol>http://|https://)"
    r"(?P<host>youtu(be)?\.([a-z]){2,3})"
    r"(?P<query>[a-z/?=]+)"
    r"(?P<videoId>[a-zA-Z0-9-_]{11})"
    r"(?P<rest>\?[a-z0-9&-_=]+)?"
    r"(?P<trailing>\&gt;|\)|\]|\}|\"|\'|$|\s)",
    '</span><br/>\n<iframe width="462" height="260" '
    'src="https://www.youtube.com/embed/\g<videoId>" '
    'frameborder="0" allowfullscreen="allowfullscreen"></iframe><br/>\n<span class="line">', 25)
