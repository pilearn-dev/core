PiJS.extend("topbar", {
  classes: {
    menu: ".js--topbar-menu",
    user: ".js--topbar-user",
    inbox: ".js--topbar-inbox",
    repaudit: ".js--topbar-rep-audit"
  },
  menu_items: [
    {"title": "Startseite", "url": "/"},
    {"title": "Forum", "url": "/f/0"},
    {"title": "Kurse", "url": "/courses"},
    {"title": "Moderation", "url": "/review"}
  ],
  init: function() {
    $(PiJS.topbar.classes.menu).on("click", function () {
      if(PiJS.topbar.close_dialog("menu")) {
        return;
      }
      $this = $(this);
      pos = this.getBoundingClientRect();
      x = pos.left;
      y = pos.bottom;

      var dialog = $("<div class='_floatbox fs-base3 s3 p-f -no-border -no-round js--topbar-dialog js--topbar-dialog-menu'>");
      dialog.css({left:x+"px", top:y+"px"});

      list = $("<div class='_nav _nav-v p2'>");
      for (var i = 0; i < PiJS.topbar.menu_items.length; i++) {
        item = PiJS.topbar.menu_items[i];
        list.append(
          $("<a>").attr("href", item.url).text(item.title)
        );
      }

      dialog.append(list);
      $(document.body).append(dialog);
    })

    $(PiJS.topbar.classes.user).on("click", function (e) {
      if(PiJS.topbar.close_dialog("user")) {
        return false;
      }
      $this = $(this);
      pos = this.getBoundingClientRect();
      x = $(window).width() - pos.right;
      y = pos.bottom;

      var dialog = $("<div class='_floatbox _dialog-limited _dialog-largest p2 p-f -no-round js--topbar-dialog js--topbar-dialog-user'>");
      dialog.html("Lade <a href='" + $this.attr("href") + "'>Mein Profil</a> ...");
      $(document.body).append(dialog);
      if((pos.left - dialog.width()) >= 0)
        dialog.css({right:x+"px", top:y+"px"});
      else
        dialog.css({left: "0", right:"0", top:y+"px"});

      $.ajax({
        url: "/topbar/user-info",
        timeout: 7000,
        success: function( result ) {
          dialog.removeClass("p2");
          dialog.html(result);
        },
        error: function() {
          window.location.href = $this.attr("href");
        }
      });

      return false;
    })

    $(PiJS.topbar.classes.inbox).on("click", function (e) {
      if(PiJS.topbar.close_dialog("inbox")) {
        return false;
      }
      $this = $(this);
      pos = this.getBoundingClientRect();
      x = $(window).width() - pos.right;
      y = pos.bottom;

      var dialog = $("<div class='_floatbox _dialog-limited _dialog-large p-f -no-round js--topbar-dialog js--topbar-dialog-inbox'>");
      dialog.html("<div class='_floatbox-header bg-dark-ll'>Lade Posteingang ...</div>");
      $(document.body).append(dialog);
      if((pos.left - dialog.width()) >= 0)
        dialog.css({right:x+"px", top:y+"px"});
      else
        dialog.css({left: "0", right:"0", top:y+"px"});

      $.ajax({
        url: "/topbar/inbox",
        success: function( result ) {
          dialog.html(result);
          updateTopbar(true);
        },
        error: function() {
          PiJS.topbar.close_dialog("inbox")
        }
      });

      return false;
    })

    $(PiJS.topbar.classes.repaudit).on("click", function (e) {
      if(PiJS.topbar.close_dialog("rep-audit")) {
        return false;
      }
      $this = $(this);
      pos = this.getBoundingClientRect();
      x = $(window).width() - pos.right;
      y = pos.bottom;

      var dialog = $("<div class='_floatbox _dialog-limited _dialog-large p-f -no-round js--topbar-dialog js--topbar-dialog-rep-audit'>");
      dialog.html("<div class='_floatbox-header bg-dark-ll'>Lade Auszeichnungen ...</div>");
      $(document.body).append(dialog);
      if((pos.left - dialog.width()) >= 0)
        dialog.css({right:x+"px", top:y+"px"});
      else
        dialog.css({left: "0", right:"0", top:y+"px"});

      $.ajax({
        url: "/topbar/rep-audit",
        success: function( result ) {
          dialog.html(result);
          updateTopbar(true);
        },
        error: function() {
          PiJS.topbar.close_dialog("rep-audit")
        }
      });

      return false;
    })

    // Only start topbar update queue, if there is a
    // achievements (rep&badges) item in the topbar,
    // i.e. the user is logged in.
    if($(PiJS.topbar.classes.repaudit).length != 0)
      setInterval(function () {updateTopbar()}, 2000);
  },
  close_dialog: function (x) {
    d = $(".js--topbar-dialog");
    val = d.hasClass("js--topbar-dialog-"+x);
    d.remove();
    return val;
  }
});

function updateTopbar(force) {
  if(((localStorage["pilearn-top:last_update"]||0) < Date.now() - 20000) || force) {
    localStorage["pilearn-top:last_update"] = Date.now();
    $.ajax({
      url: "/topbar/Update",
      success: function( result ) {
        updateTopbarWithData(result);
        localStorage["pilearn-top:restored"] = JSON.stringify(result);
      },
      error: function() {
        PiJS.topbar.close_dialog("rep-audit")
      }
    });
  } else {
    updateTopbarWithData(JSON.parse(localStorage["pilearn-top:restored"]));
  }
}

function updateTopbarWithData(result) {
  $repaudit = $(PiJS.topbar.classes.repaudit);
  $inbox = $(PiJS.topbar.classes.inbox);

  $inbox.find("._badge").remove();
  if(result.messages) {
    $inbox.prepend($('<span class="_badge _badge-s-danger -wbd p-a xa-r__sp ya-t__sp">').text(result.messages));
  }
  $repaudit.find("._badge").remove();
  if(result.reputation > 0) {
    $repaudit.prepend($('<span class="_badge _badge-s-success -wbd p-a xa-r__sp ya-t__sp">').text("+"+result.reputation));
  }
  if(result.badges) {
    $repaudit.prepend($('<span class="_badge _badge-dot-success -wbd p-a xa-r__sp ya-b__sp">neue Abzeichen</span>'));
  }
}
