jQuery.noConflict();
GSHidePost = function () {
    var hideButtons = jQuery('.hide-button');
    var dialog = jQuery('#hide-the-post');
    var loading = jQuery('#hide-the-post .loading');

    var showDialog = function(event) {
        var style  ='';
        var post = null;
        var pos = null;
        var postId = '';
        
        // Get the position of the post (hentry) that contains the
        // hide button that has been clicked.
        post = jQuery(this).parents('.hentry');
        postId = post.attr('id');
        postId = postId.slice(5);
        loading.load('../hide_post.ajax', {'form.postId': postId}, loaded);

        // TODO: Position http://api.jqueryui.com/position/
        dialog.dialog("open");
    };

    var loaded = function(response, status, request) {
        var icons = {primary: 'ui-icon-trash'};
        jQuery('#form\\.actions\\.hide').button({icons: icons, text: true});
    };
  
    return {
        init: function () {
            var hide = {icons: {primary: 'ui-icon-trash'}};

            hideButtons.removeAttr('href').click(showDialog).button(hide);

            
            dialog.dialog({autoOpen: false, closeOnEscape: true, modal: true,
                           resizable: true, title: "Hide Post",
                           minWidth: 504}); // 28u
        }
    };
}(); // GSHidePost

jQuery(document).ready( function () {
    GSHidePost.init()
});
