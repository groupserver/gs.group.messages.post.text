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
import codecs
from contextlib import contextmanager
import os
from pkg_resources import resource_filename
from unittest import TestCase
from gs.group.messages.post.text.postbody import (
    markup_youtube, markup_vimeo, split_message)


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
        'Test http://youtu.be'
        url = self.construct_url('http://youtu.be')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_youtube_com(self):
        'Test https://youtube.com'
        url = self.construct_url('https://youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertEqual('\n<iframe', r[:8])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_www_youtube_com(self):
        'Test https://www.youtube.com'
        url = self.construct_url('http://www.youtube.com')
        r = markup_youtube(None, url, [], [])
        self.assertIn('src="https://www.youtube.com/embed/qV5lzRHrGeg"', r)

    def test_https_youtu_be(self):
        'Test https://youtu.be'
        url = self.construct_url('https://youtu.be')
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


class SplitMessageTest(TestCase):
    longMessage = True

    @staticmethod
    @contextmanager
    def open_test_file(filename):
        testname = os.path.join('tests', filename)
        fullname = resource_filename('gs.group.messages.post.text', testname)
        with codecs.open(fullname, 'r', encoding='utf-8') as infile:
            yield infile

    def setUp(self):
        self.msg = ''''On Ethel the Frog tonight we look at violence: the violence of British
Gangland. Last Tuesday a reign of terror was ended when the notorious
Piranha Brothers, Dug and Dinsdale \u2014 after one the of most
extraordinary trials in British legal history \u2014 were sentenced to
400 years imprisonment for crimes of violence.'''

        self.ftr = '\n\n--\nEthel the frog'
        self.bottomQuoting = '\n\nSomeone wrote:\n> Je ne ecrit pas français.\n> Desole.\n'

    def create_ftr(self, sep):
        retval = self.ftr.replace('-', sep)
        return retval

    def assertSplit(self, intro, footer, splitMessage):
        self.assertEqual(2, len(splitMessage), 'splitMessage instance is not of lengh 2')
        self.assertEqual(splitMessage.intro, splitMessage[0])
        self.assertEqual(splitMessage.remainder, splitMessage[1])
        self.assertMultiLineEqual(intro.strip(), splitMessage.intro.strip(), 'Bodies do not match')
        self.assertMultiLineEqual(footer.strip(), splitMessage.remainder.strip(),
                                  'Footer does not match')

    def test_no_split(self):
        'Test when there is no split'
        r = split_message(self.msg)
        self.assertSplit(self.msg, '', r)

    def test_footer(self):
        'Test a split of a footer'
        m = self.msg + self.ftr
        r = split_message(m)
        self.assertSplit(self.msg, self.ftr, r)

    def test_footer_twiddle(self):
        'Test a split of a footer when ``~`` is used as the seperator'
        ftr = self.create_ftr('~')
        m = self.msg + ftr
        r = split_message(m)
        self.assertSplit(self.msg, ftr, r)

    def test_footer_equal(self):
        'Test a split of a footer when ``=`` is used as the seperator'
        ftr = self.create_ftr('=')
        m = self.msg + ftr
        r = split_message(m)
        self.assertSplit(self.msg, ftr, r)

    def test_footer_underscore(self):
        'Test a split of a footer when ``_`` is used as the seperator'
        ftr = self.create_ftr('_')
        m = self.msg + ftr
        r = split_message(m)
        self.assertSplit(self.msg, ftr, r)

    def test_footer_dash_space(self):
        'Test a split of a footer when ``- -`` is used as the seperator'
        ftr = self.ftr.replace('--', '- -')
        m = self.msg + ftr
        r = split_message(m)
        self.assertSplit(self.msg, ftr, r)

    def test_quote_inline(self):
        'Test that an inline quote is left at the start of the message'
        start = 'Someone wrote:\n> Je ne ecrit pas français.\n\n'
        msg = start + self.msg
        r = split_message(msg)
        self.assertSplit(msg, '', r)

    def test_quote_inline_footer(self):
        'Test that an inline quote is left at the start of the message, but the footer is removed'
        start = 'Someone wrote:\n> Je ne ecrit pas français.\n\n'
        body = start + self.msg
        msg = body + self.ftr
        r = split_message(msg)
        self.assertSplit(body, self.ftr, r)

    def test_bottom_quote_angle(self):
        'Test bottom quoting when it uses angle brackets'
        body = '\n'.join((self.msg, self.msg, self.msg, self.msg))
        msg = body + self.bottomQuoting
        r = split_message(msg, max_consecutive_comment=1)
        self.maxDiff = None
        self.assertSplit(body, self.bottomQuoting, r)

    def test_bottom_quote_dash(self):
        'Test bottom quoting when it uses an initial dash'
        body = '\n'.join((self.msg, self.msg, self.msg, self.msg))
        end = self.bottomQuoting.replace('Some', '-- Some')
        msg = body + end
        r = split_message(msg, max_consecutive_comment=1)
        self.assertSplit(body, end, r)

    def test_bottom_quote_ugly(self):
        'Test when good quotes go bad'
        with self.open_test_file('piranah.txt') as infile:
            msg = infile.read()
        # One of the lines
        #     On  9/17/2015 11:14 AM, Dinsdale Piranha
        # is expected to move from the footer to the body
        splitMsg = msg.split('\n')
        expectedBody = '\n'.join(splitMsg[:12])
        expectedEnd = '\n'.join(splitMsg[12:])
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_long_lines(self):
        '''Test a post by Kathleen Murphy to the St Paul Issue Forum, which has long lines.
<http://forums.e-democracy.org/r/post/7pQkztAeqn1IW8yvLEmXX6>'''
        with self.open_test_file('edem-spif-kathleenmurpy.txt') as infile:
            msg = infile.read()
        splitMsg = msg.split('\n')
        expectedBody = '\n'.join(splitMsg[:6])
        expectedEnd = '\n'.join(splitMsg[6:])
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_steve(self):
        '''Test a post from Steve to GroupServer development
<http://groupserver.org/r/topic/1lgYbWTDPFvK76GHdXr0g2>'''
        with self.open_test_file('groupserver-devel-steve.txt') as infile:
            msg = infile.read()
        r = split_message(msg)
        splitMsg = msg.split('\n')
        expectedBody = '\n'.join(splitMsg[:23])
        expectedEnd = '\n'.join(splitMsg[23:])
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_lao_tse(self):
        '''Test a quote from Lao Tse, which has a corner case signature sans a final newline'''
        with self.open_test_file('without-action.txt') as infile:
            msg = infile.read()
        expectedBody = msg
        expectedEnd = ''
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_john_brunner(self):
        '''Test a quote from John Brunner, which has a short sign-off sans a final newline'''
        with self.open_test_file('shockwave-rider.txt') as infile:
            msg = infile.read()
        expectedBody = msg
        expectedEnd = ''
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)
