# coding=utf-8
from gs.group.member.base.utils import user_admin_of_group


def can_hide_post(userInfo, groupInfo, postInfo):
    admin = user_admin_of_group(userInfo, groupInfo)
    author = user_author_of_post(userInfo, postInfo)
    retval = admin or author
    assert type(retval) == bool
    return retval


def user_author_of_post(userInfo, postInfo):
    return userInfo.id == postInfo['author_id']
