$(".js--uploader .js--uploader-tab-upload, .js--uploader .js--uploader-tab-select").click(function() {
  $(".js--uploader .js--uploader-tab-upload").toggleClass("-active");
  $(".js--uploader .js--uploader-tab-select").toggleClass("-active");
  $(".js--uploader .js--uploader-view-upload").toggleClass("hide");
  $(".js--uploader .js--uploader-view-select").toggleClass("hide");
})
