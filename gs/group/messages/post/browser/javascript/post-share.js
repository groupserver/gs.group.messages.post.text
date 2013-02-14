jQuery.noConflict();

function init_post_share() {
    var isPublic = true;
    jQuery('.gs-content-js-share').each(function () {
        shareWidget = GSShareBox(this, isPublic);
        shareWidget.init();
    });
}

jQuery(window).load(function(){
    gsJsLoader.with_module('/++resource++gs-content-js-sharebox-min-20130114.js',
                           init_post_share);
});