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
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Unauthorized
from zope.cachedescriptors.property import Lazy
from Products.XWFMailingListManager.queries import MessageQuery
from gs.group.base.page import GroupPage
from gs.group.privacy import GroupVisibility
from .error import NoIDError


class GSPostView(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.postId = self.request.get('postId', None)
        if not self.postId:
            raise NoIDError('No ID Specified')

    @Lazy
    def isPublic(self):
        assert self.groupInfo.groupObj, 'No group in the groupInfo!'
        retval = GroupVisibility(self.groupInfo).isPublic
        assert type(retval) == bool
        return retval

    @Lazy
    def messageQuery(self):
        assert self.context, 'No context for a post!'
        retval = MessageQuery(self.context)
        assert retval
        return retval

    @Lazy
    def topicTitle(self):
        retval = self.post.get('subject', '')
        return retval

    @Lazy
    def shortTopicName(self):
        '''The short name of the topic, for the breadcrumb trail.'''
        ts = self.topicTitle.split(' ')
        if len(ts) < 4:
            retval = self.topicTitle
        else:
            retval = ' '.join(ts[:3]) + '&#8230;'
        assert retval, 'There is no retval'
        return retval

    @Lazy
    def post(self):
        retval = self.messageQuery.post(self.postId)
        if not retval:
            raise NotFound(self, self.postId, self.request)
        if retval['group_id'] != self.groupInfo.id:
            m = 'You are not authorized to access this post from the '\
                'group {0}'
            msg = m.format(self.groupInfo.name)
            raise Unauthorized(msg)
        assert retval
        return retval

    @Lazy
    def relatedPosts(self):
        retval = self.messageQuery.topic_post_navigation(self.postId)
        return retval
