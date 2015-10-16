# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2015 OnlineGroups.net and Contributors.
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
from mock import MagicMock, patch
from unittest import TestCase
from gs.group.messages.post.text.viewlet import (TextPostViewlet, )


class TestTextPostViewlet(TestCase):

    def setUp(self):
        self.viewlet = TextPostViewlet(MagicMock(), MagicMock(), MagicMock(), MagicMock())

    @patch.object(TextPostViewlet, 'groupInfo')
    @patch.object(TextPostViewlet, 'loggedInUser')
    def test_show_visible(self, m_loggedInUser, m_groupInfo):
        'Test the post is shown if it is visible'
        self.viewlet.manager.post = {'hidden': False}
        r = self.viewlet.show

        self.assertTrue(r)

    @patch.object(TextPostViewlet, 'groupInfo')
    @patch.object(TextPostViewlet, 'loggedInUser')
    def test_show_hidden(self, m_loggedInUser, m_groupInfo):
        'Test that the post is hidden if it hidden'
        self.viewlet.manager.post = {'hidden': True}
        r = self.viewlet.show

        self.assertFalse(r)
