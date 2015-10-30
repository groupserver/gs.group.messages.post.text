# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
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
from mock import patch
from unittest import TestCase
from gs.group.list.email.html.matcher import (emailMatcher, )
from gs.group.messages.post.text.postbody import OnlineHTMLBody
from gs.group.privacy import (PERM_ANN, PERM_GRP, )


class OnlineHTMLBodyTest(TestCase):
    @patch('gs.group.messages.post.text.postbody.get_visibility')
    def test_public(self, mocked_get_visibility):
        r = OnlineHTMLBody('Tonight on Ethyl the Frog', PERM_ANN, [])
        self.assertNotIn(emailMatcher, r.matchers)

    @patch('gs.group.messages.post.text.postbody.get_visibility')
    def test_not_public(self, mocked_get_visibility):
        r = OnlineHTMLBody('Tonight on Ethyl the Frog', PERM_GRP, [])
        self.assertIn(emailMatcher, r.matchers)
