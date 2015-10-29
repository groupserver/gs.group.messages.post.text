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
from gs.group.messages.post.text.matcher import (START, END, youTubeMatcher, vimeoMatcher,
                                                 publicEmailMatcher)


class TestYouTubeMatcher(TestCase):
    @staticmethod
    def construct_url(prefix):
        return '{0}/watch?v=qV5lzRHrGeg'.format(prefix)

    def assertEmbed(self, uri):
        self.assertEqual(START, uri[:len(START)])
        self.assertEqual(END, uri[-len(END):])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', uri)

    def test_no_match(self):
        'Ensuring that something that is not a YouTube URL is skipped'
        r = youTubeMatcher.match("*this*")
        self.assertIs(None, r)

    def test_http_match(self):
        'Test that "http://youtube.com/" is recognised'
        url = self.construct_url('http://youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_http_sub(self):
        'Test that "http://youtube.com/" is embedded.'
        url = self.construct_url('http://youtube.com')
        r = youTubeMatcher.sub(url)
        self.assertEmbed(r)

    def test_https_match(self):
        'Test that "https://youtube.com/" is recognised'
        url = self.construct_url('https://youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_https_sub(self):
        'Test that "https://youtube.com/" is embedded.'
        url = self.construct_url('https://youtube.com')
        r = youTubeMatcher.sub(url)
        self.assertEmbed(r)

    def test_www_match(self):
        'Test that "http://www.youtube.com/" is recognised'
        url = self.construct_url('http://www.youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_www_sub(self):
        'Test that "http://www.youtube.com/" is embedded'
        url = self.construct_url('http://www.youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_https_www_match(self):
        'Test that "https://www.youtube.com/" is recognised'
        url = self.construct_url('https://www.youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_https_www_sub(self):
        'Test that "https://www.youtube.com/" is embedded'
        url = self.construct_url('https://www.youtube.com')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_youtu_be_match(self):
        'Test if http://youtu.be matches'
        url = self.construct_url('http://youtu.be')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_youtu_be_sub(self):
        'Test if http://youtu.be is embedded'
        url = self.construct_url('http://youtu.be')
        r = youTubeMatcher.sub(url)
        self.assertEmbed(r)

    def test_https_youtu_be_match(self):
        'Test if https://youtu.be matches'
        url = self.construct_url('https://youtu.be')
        r = youTubeMatcher.match(url)
        self.assertTrue(r)

    def test_https_youtu_be_sub(self):
        'Test if https://youtu.be is embedded'
        url = self.construct_url('https://youtu.be')
        r = youTubeMatcher.sub(url)
        self.assertEmbed(r)


class TestVimeoMatcher(TestCase):
    @staticmethod
    def construct_url(prefix):
        return '{0}/118019156'.format(prefix)

    def assertEmbed(self, uri):
        self.assertEqual(START, uri[:len(START)])
        self.assertEqual(END, uri[-len(END):])
        self.assertIn('src="https://player.vimeo.com/video/118019156?', uri)

    def test_no_match(self):
        'Ensuring that something that is not a Vimeo URL is skipped'
        r = vimeoMatcher.match("*this*")
        self.assertIs(None, r)

    def test_vimeo_com_match(self):
        'Test http://vimeo.com is matched'
        url = self.construct_url('http://vimeo.com')
        r = vimeoMatcher.match(url)
        self.assertTrue(r)

    def test_vimeo_com_embed(self):
        'Test http://vimeo.com is embedded'
        url = self.construct_url('http://vimeo.com')
        r = vimeoMatcher.sub(url)
        self.assertEmbed(r)

    def test_https_vimeo_com_match(self):
        'Test https://vimeo.com is matched'
        url = self.construct_url('https://vimeo.com')
        r = vimeoMatcher.match(url)
        self.assertTrue(r)

    def test_https_vimeo_com_embed(self):
        'Test https://vimeo.com is embedded'
        url = self.construct_url('https://vimeo.com')
        r = vimeoMatcher.sub(url)
        self.assertEmbed(r)

    def test_wwww_vimeo_com_match(self):
        'Test http://www.vimeo.com is matched'
        url = self.construct_url('http://wwww.vimeo.com')
        r = vimeoMatcher.match(url)
        self.assertTrue(r)

    def test_www_vimeo_com_embed(self):
        'Test http://wwww.vimeo.com is embedded'
        url = self.construct_url('http://wwww.vimeo.com')
        r = vimeoMatcher.sub(url)
        self.assertEmbed(r)

    def test_https_wwww_vimeo_com_match(self):
        'Test https://www.vimeo.com is matched'
        url = self.construct_url('https://wwww.vimeo.com')
        r = vimeoMatcher.match(url)
        self.assertTrue(r)

    def test_https_www_vimeo_com_embed(self):
        'Test https://wwww.vimeo.com is embedded'
        url = self.construct_url('https://wwww.vimeo.com')
        r = vimeoMatcher.sub(url)
        self.assertEmbed(r)


class TestPublicEmailMatcher(TestCase):
    def test_not_email(self):
        r = publicEmailMatcher.match('This is not an email')
        self.assertIsNone(r)

    def test_email_match(self):
        r = publicEmailMatcher.match('person@example.com')
        self.assertTrue(r)

    def test_email_sub(self):
        e = 'person@example.com'
        r = publicEmailMatcher.sub(e)
        self.assertNotIn(e, r)
