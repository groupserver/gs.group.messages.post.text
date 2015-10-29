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
from __future__ import absolute_import, unicode_literals, print_function
from unittest import TestCase
from gs.group.messages.post.text.matcher import (youTubeMatcher, )


class TestYouTubeMatcher(TestCase):
    @staticmethod
    def construct_url(prefix):
        return '{0}/watch?v=qV5lzRHrGeg'.format(prefix)

    def assertEmbed(self, uri):
        self.assertIn('\n<iframe', uri)
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', uri)

    def test_http_match(self):
        'Test that "http://youtube.com/" is recognised'
        r = youTubeMatcher.match("*this*")
        self.assertIs(None, r)

        url = self.construct_url('http://youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_http_sub(self):
        'Test that "http://youtube.com/" is embedded.'
        url = self.construct_url('http://youtube.com')
        r = youTubeMatcher.sub(url)
        self.assertEmbed(r)
