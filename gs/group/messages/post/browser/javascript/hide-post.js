jQuery.noConflict();
GSHidePost = function () {
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
                                                                                                 
    pos = post.position();
    // Position the Hide UI over the post.
    style = style + 'top:'+ pos.top+'px;display:block;';
    jQuery('#hide-the-post')
      .attr('style', style);
    jQuery("#hide-the-post").load('../hide_post.ajax', {'form.postId': postId});
  };
  
  return {
    init: function () {
      jQuery('.hide-button')
        .removeAttr('href')
        .click(showDialog);
      }
  };
}(); // GSHidePost

jQuery(document).ready( function () {
  GSHidePost.init()
});

