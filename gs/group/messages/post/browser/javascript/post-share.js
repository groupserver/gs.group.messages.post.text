jQuery.noConflict();

function gs_group_messages_post_share_init() {
    var isPublic = false, shareWidget = null;

    jQuery('.gs-content-js-share').each(function() {
        // TODO: make isPublic not sux. This is the one topic-specific part.
        isPublic = Boolean(Number(jQuery(this).attr('public')));
        shareWidget = GSShareBox(this, isPublic);
        shareWidget.init();
    });
}

jQuery(window).load(function () {
    gsJsLoader.with_module('/++resource++gs-content-js-sharebox-20130305.js',
                           gs_group_messages_post_share_init);
});
