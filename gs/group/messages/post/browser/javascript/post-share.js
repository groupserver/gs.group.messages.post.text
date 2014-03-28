"use strict";
// Sharing a post
//
// Copyright © 2013, 2014 OnlineGroups.net and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
// FOR A PARTICULAR PURPOSE.
//
jQuery.noConflict();

function gs_group_messages_post_share_init() {
    var isPublic=false, shareWidget=null;

    jQuery('.gs-content-js-share').each(function() {
        // TODO: make isPublic not sux. This is the one topic-specific part.
        isPublic = Boolean(Number(jQuery(this).attr('public')));
        shareWidget = GSShareBox(this, isPublic);
        shareWidget.init();
    });
}

jQuery(window).load(function () {
    gsJsLoader.with_module('/++resource++gs-content-js-sharebox-min-20140327.js',
                           gs_group_messages_post_share_init);
});
