jQuery.noConflict();
var GSHidePost = function() {
    var hideButtons = jQuery('.hide-button'), dialog = jQuery('#hide-the-post')
        loading = jQuery('#hide-the-post .loading');

    function showDialog(event) {
        var style  ='', post = null, pos = null, postId = '';
        
        // Get the position of the post (hentry) that contains the
        // hide button that has been clicked.
        post = jQuery(this).parents('.hentry');
        postId = post.attr('id');
        postId = postId.slice(5);
        dialog.data('postId', postId);
        dialog.modal('show');
    };

    function shown(event) {
        var postId = null;
        postId = jQuery(this).data('postId');
        loading.load('../hide_post.ajax', {'form.postId': postId}, loaded);
    };
    function loaded(response, status, request) {
        var b = null;
        b = jQuery('#form\\.actions\\.hide');
        b.button();
    };
  
    return {
        init: function () {
            hideButtons.click(showDialog);
            dialog.on('shown', shown);
        }
    };
}(); // GSHidePost

jQuery(window).load( function () {
    GSHidePost.init()
});
