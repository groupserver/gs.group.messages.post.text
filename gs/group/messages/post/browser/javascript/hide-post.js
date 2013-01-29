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
        dialog.data('postId', postId);
        dialog.modal('show');
    };

    var shown = function(event) {
        var postId = null;
        postId = jQuery(this).data('postId');
        loading.load('../hide_post.ajax', {'form.postId': postId}, loaded);
    };
    var loaded = function(response, status, request) {
    };
  
    return {
        init: function () {
            hideButtons.click(showDialog);
            dialog.on('shown', shown);
        }
    };
}(); // GSHidePost

jQuery(document).ready( function () {
    GSHidePost.init()
});
