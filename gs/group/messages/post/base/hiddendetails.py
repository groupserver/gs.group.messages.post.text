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
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from .queries import PostQuery


class HiddenPostInfo(object):
    def __init__(self, context, postId):
        if not context:
            raise ValueError('No context')
        self.context = context
        if not postId:
            raise ValueError('No post identifier')
        if not isinstance(postId, basestring):
            raise TypeError('Post identifier not a string')
        self.postId = postId

    @Lazy
    def query(self):
        retval = PostQuery()
        return retval

    @Lazy
    def hiddenPostDetails(self):
        retval = self.query.get_hidden_post_details(self.postId)
        if not retval:
            m = 'No details for the hidden post "{0}"'
            msg = m.format(self.postId)
            raise ValueError(msg)
        return retval

    @Lazy
    def adminInfo(self):
        retval = createObject('groupserver.UserFromId', self.context,
                              self.hiddenPostDetails['hiding_user'])
        return retval

    @Lazy
    def date(self):
        retval = self.hiddenPostDetails['date_hidden']
        return retval

    @Lazy
    def reason(self):
        retval = self.hiddenPostDetails['reason']
        return retval
