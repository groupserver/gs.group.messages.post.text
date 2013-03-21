jQuery.noConflict();var GSHidePost=function(){var e=jQuery(".hide-button"),c=jQuery("#hide-the-post");
loading=jQuery("#hide-the-post .loading");function a(h){var g=null,f="";g=jQuery(this).parents(".hentry");
f=g.attr("id");f=f.slice(5);c.data("postId",f);c.modal("show")}function d(g){var f=null;
f=jQuery(this).data("postId");loading.load("../hide_post.ajax",{"form.postId":f},b)
}function b(h,g,i){var f=null;f=jQuery("#form\\.actions\\.hide");f.button()}return{init:function(){e.click(a);
c.on("shown",d)}}}();jQuery(window).load(function(){GSHidePost.init()});