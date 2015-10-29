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
from gs.group.messages.post.text.splitmessage import (split_message, SplitMessage, )


class SplitMessageTest(TestCase):
    longMessage = True

    @staticmethod
    @contextmanager
    def open_test_file(filename):
        testname = os.path.join('tests', filename)
        fullname = resource_filename('gs.group.messages.post.text', testname)
        with codecs.open(fullname, 'r', encoding='utf-8') as infile:
            yield infile

    @staticmethod
    def expected_split(msg, line):
        '''Create a split at the expected line'''
        splitMsg = msg.strip().split('\n')
        expectedBody = '\n'.join(splitMsg[:line])
        expectedEnd = '\n'.join(splitMsg[line:])
        retval = SplitMessage(expectedBody, expectedEnd)
        return retval

    def setUp(self):
        self.msg = '''On Ethel the Frog tonight we look at violence: the violence of British
Gangland. Last Tuesday a reign of terror was ended when the notorious
Piranha Brothers, Dug and Dinsdale \u2014 after one the of most
extraordinary trials in British legal history \u2014 were sentenced to
400 years imprisonment for crimes of violence.\n'''

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
        body = (4 * self.msg)
        msg = body + self.bottomQuoting
        r = split_message(msg, max_consecutive_comment=1)
        self.assertSplit(body, self.bottomQuoting, r)

    def test_bottom_quote_dash(self):
        'Test bottom quoting when it uses an initial dash'
        body = (4 * self.msg)
        end = self.bottomQuoting.replace('Some', '-- Some')
        msg = body + end
        r = split_message(msg, max_consecutive_comment=1)
        self.assertSplit(body, end, r)

    def test_whitespace_split(self):
        '''Test when whitespace indicates a split.'''
        body = (4 * self.msg)
        mw = 3
        end = ((mw + 1) * '\n') + 'A. Person <http://example.com/a.person>\n'
        msg = body + end
        r = split_message(msg, max_consecutive_whitespace=mw)
        self.assertSplit(body, end, r)

    def test_whitespace_no_split(self):
        '''Test when whitespace does not indicate a split.'''
        body = (4 * self.msg)
        mw = 3
        end = (mw * '\n') + 'A. Person <http://example.com/a.person>\n'
        msg = body + end
        r = split_message(msg, max_consecutive_whitespace=mw)
        self.assertSplit(msg, '', r)

    def test_multiple_quote_split(self):
        '''Test when multiple quotes, at the bottom after a long intro, indicate a split'''
        quotedLines = ['> ' + line for line in self.msg.split('\n')]
        mq = 10
        end = '\n'.join((quotedLines + quotedLines + quotedLines)[:(mq + 1)]) + '\n'
        body = (6 * self.msg)  # Nice and long
        msg = '\n'.join((body, end))
        r = split_message(msg, max_consecutive_comment=mq)
        self.assertSplit(body, end, r)

    def test_multiple_quote_further_info(self):
        '''Test multiple quotes when further info does not indicate a split'''
        quotedLines = ['> ' + line for line in self.msg.split('\n')]
        mq = 5
        end = '\n'.join((quotedLines + quotedLines + quotedLines)[:mq]) + '\n'
        body = (6 * self.msg)  # Nice and long
        msg = '\n'.join((body, end, self.msg))
        r = split_message(msg, max_consecutive_comment=mq)
        self.assertSplit(msg, '', r)

    def test_bottom_quote_ugly(self):
        'Test when good quotes go bad'
        with self.open_test_file('piranah.txt') as infile:
            msg = infile.read()
        # One of the lines
        #     On  9/17/2015 11:14 AM, Dinsdale Piranha
        # is expected to move from the footer to the body
        expected = self.expected_split(msg, 12)
        r = split_message(msg)
        self.assertSplit(expected.intro, expected.remainder, r)

    def test_long_lines(self):
        '''Test a post by Kathleen Murphy to the St Paul Issue Forum, which has long lines.
<http://forums.e-democracy.org/r/post/7pQkztAeqn1IW8yvLEmXX6>'''
        with self.open_test_file('edem-spif-kathleenmurpy.txt') as infile:
            msg = infile.read()
        expected = self.expected_split(msg, 6)
        r = split_message(msg)
        self.assertSplit(expected.intro, expected.remainder, r)

    def test_steve(self):
        '''Test a post from Steve to GroupServer development
<http://groupserver.org/r/topic/1lgYbWTDPFvK76GHdXr0g2>'''
        with self.open_test_file('groupserver-devel-steve.txt') as infile:

            msg = infile.read()
        expected = self.expected_split(msg, 23)
        r = split_message(msg)
        self.assertSplit(expected.intro, expected.remainder, r)

    def test_lao_tse(self):
        '''Test a quote from Lao Tse, which has a corner case signature sans a final newline'''
        with self.open_test_file('without-action.txt') as infile:
            msg = infile.read().strip()
        expectedBody = msg
        expectedEnd = ''
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_john_brunner(self):
        '''Test a quote from John Brunner, which has a short sign-off sans a final newline'''
        with self.open_test_file('shockwave-rider.txt') as infile:
            msg = infile.read().strip()
        expectedBody = msg
        expectedEnd = ''
        r = split_message(msg)
        self.assertSplit(expectedBody, expectedEnd, r)

    def test_html_spam(self):
        '''Test that we handle a spam message containing HTML well, or at least not poorly'''
        with self.open_test_file('html-spam.txt') as infile:
            msg = infile.read()
        # The split is at a closing HTML-comment "-->".
        expected = self.expected_split(msg, 14)
        r = split_message(msg)
        self.assertSplit(expected.intro, expected.remainder, r)

    def test_short_closing(self):
        '''Ensure the short closings are not snipped'''
        # --=mpj17=-- Short closings used to be snipped, but they are now kept.
        closing = '\nThanks,\n  Ethel'
        msg = self.msg + closing
        r = split_message(msg)
        self.assertSplit(msg, '', r)

    def test_very_short_closing(self):
        '''Ensure the one-line closings are not snipped'''
        # --=mpj17=-- The "--" would *normally* cause a snip, but not when there is only one line
        closing = '\n-- Ethel'
        msg = self.msg + closing
        r = split_message(msg)
        self.assertSplit(msg, '', r)
