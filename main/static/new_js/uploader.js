$(".js--uploader-img-select").click(function() {
  $this = $(this);
  sidebar = $(".js--uploader-sidebar");

  $(".js--uploader-img-select").removeClass("-active");
  $this.addClass("-active");

  sidebar.removeClass("hide");

  sidebar.find("#js--uploader-name").val($this.attr("data-url"));
});

$(".js--uploader .js--uploader-tab-upload, .js--uploader .js--uploader-tab-select").click(function() {
  $(".js--uploader .js--uploader-tab-upload").toggleClass("-active");
  $(".js--uploader .js--uploader-tab-select").toggleClass("-active");
  $(".js--uploader .js--uploader-view-upload").toggleClass("hide");
  $(".js--uploader .js--uploader-view-select").toggleClass("hide");
});
