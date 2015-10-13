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
from __future__ import absolute_import, division, unicode_literals, print_function
from gs.group.messages.post.base import PostViewlet
from .postbody import split_message


class TextPostViewlet(PostViewlet):

    def update(self):
        super(TextPostViewlet, self).update()
        self.postIntro, self.postRemainder = split_message(self.post['body'])

    @property
    def show(self):
        retval = self.manager.post.hidden
        assert type(retval) == bool, 'self.manager.post.hidden is not a Boolean'
        return retval
