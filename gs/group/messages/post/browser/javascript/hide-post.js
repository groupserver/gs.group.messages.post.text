"use strict";
// Hiding a post
//
// Copyright © 2011, 2012, 2013, 2014 OnlineGroups.net and Contributors.
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
function GSHidePost(hideButtonsSelector, dialogSelector, loadingSelector) {
    var hideButtons=null, dialog=null, loading=null, URL='../hide_post.ajax';

    function showDialog(event) {
        var post=null, postId='';
        
        // Get the position of the post (hentry) that contains the
        // hide button that has been clicked.
        post = jQuery(this).parents('.hentry');
        postId = post.attr('id');
        postId = postId.slice(5);
        dialog.data('postId', postId);
        dialog.modal('show');
    }

    function shown(event) {
        var postId=null;
        postId = jQuery(this).data('postId');
        loading.load(URL, {'form.postId': postId}, loaded);
    }

    function loaded(response, status, request) {
        var b=null;
        b = jQuery('#form\\.actions\\.hide');
        b.button();
    }

    function setup() {
        hideButtons = jQuery(hideButtonsSelector);
        dialog = jQuery(dialogSelector);
        loading = jQuery(loadingSelector);
    }
    setup();  // Note: automatic execution
  
    return {
        init: function () {
            hideButtons.click(showDialog);
            dialog.on('shown', shown);
        }
    };
}  // GSHidePost

jQuery(window).load( function () {
    var hider=null;
    hider = GSHidePost('.hide-button', '#hide-the-post', 
                       '#hide-the-post-loading');
    hider.init();
});
