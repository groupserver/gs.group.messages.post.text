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
from operator import and_
import sqlalchemy as sa
from datetime import datetime
from pytz import UTC
from zope.sqlalchemy import mark_changed
from gs.database import getSession, getTable


class PostQuery(object):
    def __init__(self, context=None):
        self.postTable = getTable('post')
        self.hiddenPostTable = getTable('hidden_post')
        self.topicTable = getTable('topic')

    def get_hidden_post_details(self, postId):
        s = self.hiddenPostTable.select()
        s = s.order_by(sa.desc(self.hiddenPostTable.c.date_hidden))
        s.append_whereclause(self.hiddenPostTable.c.post_id == postId)

        retval = None
        session = getSession()
        r = session.execute(s)
        if r.rowcount >= 1:
            row = r.fetchone()
            retval = {
                'post_id': row['post_id'],
                'date_hidden': row['date_hidden'],
                'hiding_user': row['hiding_user'],
                'reason': row['reason']}
        return retval

    def hide_post(self, postId, userId, reason):
        now = datetime.now(UTC)
        self.update_post_table(postId, now)
        self.update_hidden_post_table(postId, now, userId, reason)

    def update_post_table(self, postId, dt):
        u = self.postTable.update(self.postTable.c.post_id == postId)
        session = getSession()
        d = {'hidden': dt}
        session.execute(u, params=d)
        mark_changed(session)

    def update_hidden_post_table(self, postId, dt, userId, reason):
        i = self.hiddenPostTable.insert()
        session = getSession()
        d = {'post_id': postId,
             'date_hidden': dt,
             'hiding_user': userId,
             'reason': reason}
        session.execute(i, params=d)
        mark_changed(session)

    def all_posts_in_topic_hidden(self, postId):
        s1 = sa.select([self.postTable.c.topic_id])
        s1.append_whereclause(self.postTable.c.post_id == postId)
        ss = s1.alias('ss')

        s2 = sa.select([self.postTable.c.hidden])
        s2.append_whereclause(self.postTable.c.topic_id == ss.c.topic_id)

        session = getSession()
        r = session.execute(s2)
        retval = reduce(and_, [bool(x['hidden']) for x in r], True)
        return retval

    def hide_topic(self, postId):
        session = getSession()
        s1 = sa.select([self.postTable.c.topic_id])
        s1.append_whereclause(self.postTable.c.post_id == postId)
        r = session.execute(s1)
        t = r.fetchone()['topic_id']

        u = self.topicTable.update(t == self.topicTable.c.topic_id)
        now = datetime.now(UTC)
        d = {'hidden': now}
        session.execute(u, params=d)
