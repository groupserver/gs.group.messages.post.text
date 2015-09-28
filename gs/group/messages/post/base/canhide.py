# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2011, 2012, 2013, 2014, 2015 OnlineGroups.net and
# Contributors.
#
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
from gs.group.member.base import user_admin_of_group


def can_hide_post(userInfo, groupInfo, postInfo):
    admin = user_admin_of_group(userInfo, groupInfo)
    author = user_author_of_post(userInfo, postInfo)
    retval = admin or author
    assert type(retval) == bool
    return retval


def user_author_of_post(userInfo, postInfo):
    return userInfo.id == postInfo['author_id']
