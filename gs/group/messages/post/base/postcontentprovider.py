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
from __future__ import absolute_import, division, unicode_literals
from threading import RLock
import sys
if (sys.version_info >= (3, )):
    from urllib.parse import quote
else:
    from urllib import quote  # lint:ok
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.app.pagetemplate import ViewPageTemplateFile
from gs.group.base.contentprovider import GroupContentProvider
from gs.group.messages.base import get_icon
from .canhide import can_hide_post
from .postbody import get_post_intro_and_remainder
from .hiddendetails import HiddenPostInfo
from . import GSMessageFactory as _
UTF8 = 'utf-8'


class GSPostContentProvider(GroupContentProvider):
    post = None
    __thread_lock = RLock()
    cookedTemplates = {}

    def __init__(self, context, request, view):
        super(GSPostContentProvider, self).__init__(context, request, view)
        self.__updated = False
        # allow baseclass override
        self.can_hide_post = can_hide_post

    def update(self):
        """Update the internal state of the post content-provider.

        This method can be considered the main "setter" for the
        content provider; for the most part, information about the post's
        author is set.

        SIDE EFFECTS
          The following attributes are set.
            * "self.__updated"     Set to "True".
            * "self.authorId"      Set to the user-id of the post author.
            * "self.authorName"    Set to the name of the post author.
            * "self.authorExists"  Set to "True" if the author exists.
            * "self.authored"      Set to "True" if the current user
                                   authored the post.
            * "self.authorImage"   Set to the URL of the author's image.
            * "self.siteInfo"     Set to an instance of GSSiteInfo.
            * "self.groupInfo"    Set to an instance of GSGroupInfo.
            * "self.post"         Set to the content of the post.
        """
        assert self.post
        # See the interface for what is passed in.
        self.__updated = True

        self.showPhoto = self.showPhoto

        self.authored = self.user_authored()
        self.authorInfo = createObject('groupserver.UserFromId',
                                       self.context,
                                       self.post['author_id'])
        # Note: This function caches.
        ir = get_post_intro_and_remainder(self, self.post['body'])
        self.postIntro, self.postRemainder = ir
        self.cssClass = self.get_cssClass()

        self.hiddenPostDetails = None
        if self.post['hidden']:
            self.hiddenPostInfo = HiddenPostInfo(self.context,
                                                 self.post['post_id'])

        self.mediaFiles = []
        self.normalFiles = []
        for fm in self.post['files_metadata']:
            fm['icon'] = get_icon(fm['mime_type'])
            size = '{0:.1f}kb'.format(fm['file_size'] / 1024.0)
            fm['size'] = size
            # TODO: Extend to audio <https://redmine.iopen.net/issues/416>
            # TODO: Extend to video <https://redmine.iopen.net/issues/333>
            if fm['mime_type'][:5] == 'image':
                url = '{0}/messages/image/{1}'
                fm['url'] = url.format(self.groupInfo.relativeURL,
                                       fm['file_id'])
                s = '{0}/files/f/{1}/{2}'
                fm['src'] = s.format(self.groupInfo.relativeURL,
                                     fm['file_id'], fm['file_name'])
                self.mediaFiles.append(fm)
            else:
                url = '{0}/files/f/{1}/{2}'
                fm['url'] = url.format(self.groupInfo.relativeURL,
                                       fm['file_id'], fm['file_name'])
                self.normalFiles.append(fm)

        self.canHide = self.can_hide_post(self.loggedInUser, self.groupInfo,
                                          self.post)

    def cook_template(self, fname):
        if fname in self.cookedTemplates:
            return self.cookedTemplates[fname]

        cooked = ViewPageTemplateFile(fname)
        try:
            # don't block, we'll just cache it later
            if self.__thread_lock.acquire(False):
                self.cookedTemplates[fname] = cooked
        finally:
            self.__thread_lock.release()

        return cooked

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = self.cook_template(self.pageTemplateFileName)
        self.request.debug = False
        r = pageTemplate(self)
        return r

    #########################################
    # Non-standard methods below this point #
    #########################################

    def get_cssClass(self):
        assert hasattr(self, 'position')  # passed in
        retval = 'even' if ((self.position % 2) == 0) else 'odd'
        retval += ' post-hidden' if self.post['hidden'] else ' post-visible'
        return retval

    def user_authored(self):
        retval = False
        if not(self.loggedInUser.anonymous):
            retval = self.loggedInUser.id == self.post['author_id']
        assert type(retval) == bool
        return retval

    def quote(self, msg):
        assert msg
        retval = quote(msg)
        assert retval
        return retval

    @Lazy
    def loggedInUser(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        assert retval
        return retval

    @Lazy
    def hiddenSupportEmail(self):
        m = _('support-post-hidden-message',
              '''Hello,

I want to see the post at
  ${url}
However, it is hidden. I think I should be allowed to see the post
because...''',
              mapping={'url': self.request.URL})

        message = quote(m.encode(UTF8))
        s = _('support-post-hidden-subject', 'Post hidden')
        subject = quote(s.encode(UTF8))
        mailto = 'mailto:{support}?subject={subj}&body={msg}'
        retval = mailto.format(support=self.siteInfo.get_support_email(),
                               subj=subject, msg=message)
        return retval
