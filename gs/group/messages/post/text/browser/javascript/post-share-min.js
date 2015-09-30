"use strict";jQuery.noConflict();function gs_group_messages_post_share_init(){var b=false,a=null;
jQuery(".gs-content-js-share").each(function(){b=Boolean(Number(jQuery(this).attr("public")));
a=GSShareBox(this,b);a.init()})}jQuery(window).load(function(){gsJsLoader.with_module("/++resource++gs-content-js-sharebox-min-20140327.js",gs_group_messages_post_share_init)
});