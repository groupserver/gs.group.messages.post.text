# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2012, 2013, 2014 OnlineGroups.net and Contributors.
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
SUBSYSTEM = 'gs.group.messages.post'
from logging import getLogger
log = getLogger(SUBSYSTEM)
from zope.component import getMultiAdapter
from gs.core import to_ascii
from gs.group.base.page import GroupPage
from .error import NoIDError


class GSPostTraversal(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)

    def publishTraverse(self, request, name):
        if 'postId' not in request:
            self.request['postId'] = name
        return self

    def __call__(self):
        # TODO: Handle the 410 (Gone) post here. Hidden posts will
        # sometimes raise a 410
        # <https://projects.iopen.net/groupserver/ticket/316>
        try:
            retval = getMultiAdapter((self.context, self.request),
                                     name="gspost")()
        except NoIDError as n:  # lint:ok
            u = '{0}/messages/topics.html'.format(self.groupInfo.url)
            m = 'No post ID in <{0}>. Going to <{1}>'
            msg = m.format(self.request.URL, u)
            log.info(msg)
            uri = to_ascii(u)
            retval = self.request.RESPONSE.redirect(uri)
        return retval
