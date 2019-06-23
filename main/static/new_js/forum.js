$(".js--comment-area-button").click(function() {
  $this = $(this);
  post = $this.attr("data-post");
  $("#" + post + "-comment-area").toggleClass("hide")
  $this.toggleClass("hide");
})
$(".js--comment-button").click(function() {
  $this = $(this);
  post = $this.attr("data-post");
  comment = $("#" + post + "-comment-box").val()
  $("#" + post + "-comment-area").toggleClass("hide")
  $("#" + post + "-comment-area").parent().find(".js--comment-area-button").toggleClass("hide")
  $("#" + post + "-comment-box").val("");

  $.ajax({
    url: "/forum/comments/"+post+"/add",
    method: "POST",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify({ content: comment }),
    success: function( r ) {
      if(r.result == "success")
        updateComments(post);
      else
        PiJS.warnbox.error(r.error, $this.parent());
    }
  });
})

function initCommentVoting() {
  $("[data-comment-vote][data-vote-comment]").click(function() {
    $this = $(this);
    action = $this.attr("data-comment-vote");
    comment = $this.attr("data-vote-comment");
    $.ajax({
      url: "/forum/comments/"+comment+"/vote",
      method: "POST",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify({ vote: action }),
      success: function( r ) {
        if(r.result == "success") {
          if(r.deleted == 1) {
            $this.parent().parent().remove();
          } else if(action == "up") {
            $this.addClass("-active").parent().find(".js--comment-score").text(r.score);
          } else if(action == "restore") {
            $this.parent().parent().removeClass("bg-danger-ll");
            fetchComments($this.parent().parent().attr("data-comment-post"), true);
          } else {
            updateComments($this.parent().parent().attr("data-comment-post"))
          }
        } else
          PiJS.warnbox.error(r.error, $this.parent().parent());
      }
    });
  })
}
initCommentVoting();


function updateComments(post) {
  fetchComments(post, false)
}
function fetchComments(post, with_deleted) {
  $.ajax({
    url: "/forum/"+post+"/comments" + (with_deleted? "?include-deleted=yes" :""),
    method: "GET",
    contentType: "application/json; charset=utf-8",
    success: function( r ) {
      if(r.result == "success") {
        $("#"+post+"-comments").html(r.render);
        initCommentVoting();
      } else
        PiJS.warnbox.error(r.error, $this.parent());
    }
  });
}


$("[data-purge-comments]").click(function() {
  $this = $(this);
  post = $this.attr("data-purge-comments");

  $.ajax({
    url: "/forum/comments/"+post+"/purge",
    method: "POST",
    contentType: "application/json; charset=utf-8",
    success: function( r ) {
      if(r.result == "success")
        updateComments(post);
      else
        PiJS.warnbox.error(r.error, $this.parent());
    }
  });
})

$("[data-dialog][data-dialog-post]").click(function() {
  $this = $(this);
  type = $this.attr("data-dialog");
  post = $this.attr("data-dialog-post");

  PiJS.dialog.fromURL("/forum/" + post + "/dialog?type="+type, false)
})

$("[data-vote][data-vote-post]").click(function() {
  $this = $(this);
  type = $this.attr("data-vote");
  post = $this.attr("data-vote-post");


  $.ajax({
    url: "/forum/"+post+"/vote",
    method: "POST",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify({"type": type}),
    success: function( r ) {
      if(r.result == "success")
        updatePost(post, r.update);
      else
        PiJS.warnbox.error(r.error, $this.parent());
    }
  });
})

function updatePost(post, r) {
  $post = $("#"+post);
  if(typeof r.score != "undefined") {
    $post.find(".score-vote").text(r.score);
  }
  if(typeof r.vote != "undefined") {
    if(r.vote == 1) {
      $post.find(".up-vote").addClass("-active");
      $post.find(".down-vote").removeClass("-active");
    } else if (r.vote == 0) {
      $post.find(".up-vote").removeClass("-active");
      $post.find(".down-vote").removeClass("-active");
    } else if (r.vote == -1) {
      $post.find(".up-vote").removeClass("-active");
      $post.find(".down-vote").addClass("-active");
    }
  }
  if(typeof r.accepted != "undefined") {
    $(".accept-vote.-active").removeClass("-active")
    if(r.accepted != null)
      $("#" + r.accepted + " .accept-vote").addClass("-active")
  }
  if(typeof r.closevotes != "undefined") {
    $post.find("[data-dialog='close']").text("schließen (" + r.closevotes + ")");
  }
  if(typeof r.reopenvotes != "undefined") {
    $post.find("[data-vote='reopen']").text("öffnen (" + r.reopenvotes + ")");
  }
  if(typeof r.deletevotes != "undefined") {
    $post.find("[data-vote='delete']").text("löschen (" + r.deletevotes + ")");
  }
  if(typeof r.undeletevotes != "undefined") {
    $post.find("[data-vote='undelete']").text("un-löschen (" + r.undeletevotes + ")");
  }
  if(typeof r.deleted != "undefined") {
    if(post.startsWith("post-"))
      $fullpost = $("#fullpost");
    else
      $fullpost = $post;
    if(r.deleted) {
      $fullpost.addClass("bg-danger-lll");
      $post.find("[data-vote='delete']").text("un-löschen").attr("data-vote", "undelete");
    } else {
      $fullpost.removeClass("bg-danger-lll");
      $post.find("[data-vote='undelete']").text("löschen").attr("data-vote", "delete");
    }
  }
}
