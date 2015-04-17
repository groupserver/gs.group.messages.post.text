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
from unittest import TestCase
from gs.group.messages.post.postbody import (
    markup_youtube, markup_vimeo)


class YouTubeTest(TestCase):
    @staticmethod
    def construct_url(prefix):
        return '{0}/watch?v=qV5lzRHrGeg'.format(prefix)

    def test_youtube_com(self):
        'Test http://youtube.com'
        url = self.construct_url('http://youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertEqual('\n<iframe', r[:8])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_www_youtube_com(self):
        'Test http://www.youtube.com'
        url = self.construct_url('http://www.youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_youtu_be(self):
        'Test http://youtube.com'
        url = self.construct_url('http://youtu.be')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_youtube_com(self):
        'Test https://youtube.com'
        url = self.construct_url('http://youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertEqual('\n<iframe', r[:8])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_www_youtube_com(self):
        'Test https://www.youtube.com'
        url = self.construct_url('http://www.youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_youtu_be(self):
        'Test https://youtube.com'
        url = self.construct_url('http://youtu.be')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)


class VimeoTest(TestCase):
    @staticmethod
    def construct_url(prefix):
        return '{0}/118019156'.format(prefix)

    def test_vimeo_com(self):
        'Test http://vimeo.com'
        url = self.construct_url('http://vimeo.com')
        r = markup_vimeo(None, url, [], [])
        self.assertEqual('\n<iframe', r[:8])
        self.assertIn('src="https://player.vimeo.com/video/118019156?', r)

    def test_www_vimeo_com(self):
        'Test http://www.vimeo.com'
        url = self.construct_url('http://www.vimeo.com')
        r = markup_vimeo(None, url, [], [])
        self.assertIn('src="https://player.vimeo.com/video/118019156?', r)

    def test_https_vimeo_com(self):
        'Test https://vimeo.com'
        url = self.construct_url('https://vimeo.com')
        r = markup_vimeo(None, url, [], [])
        self.assertEqual('\n<iframe', r[:8])
        self.assertIn('src="https://player.vimeo.com/video/118019156?', r)

    def test_https_www_vimeo_com(self):
        'Test https://www.vimeo.com'
        url = self.construct_url('https://www.vimeo.com')
        r = markup_vimeo(None, url, [], [])
        self.assertIn('src="https://player.vimeo.com/video/118019156?', r)
