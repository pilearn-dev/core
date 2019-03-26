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
      dialog.css({right:x+"px", top:y+"px"});
      dialog.html("Lade <a href='" + $this.attr("href") + "'>Mein Profil</a> ...");

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

      $(document.body).append(dialog);
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
      dialog.css({right:x+"px", top:y+"px"});
      dialog.html("<div class='_floatbox-header bg-dark-ll'>Lade Posteingang ...</div>");

      $.ajax({
        url: "/topbar/inbox",
        success: function( result ) {
          dialog.html(result);
        },
        error: function() {
          PiJS.topbar.close_dialog("inbox")
        }
      });

      $(document.body).append(dialog);
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
      dialog.css({right:x+"px", top:y+"px"});
      dialog.html("<div class='_floatbox-header bg-dark-ll'>Lade Reputation ...</div>");

      $.ajax({
        url: "/topbar/rep-audit",
        success: function( result ) {
          dialog.html(result);
        },
        error: function() {
          PiJS.topbar.close_dialog("rep-audit")
        }
      });

      $(document.body).append(dialog);
      return false;
    })
  },
  close_dialog: function (x) {
    d = $(".js--topbar-dialog");
    val = d.hasClass("js--topbar-dialog-"+x);
    d.remove();
    return val;
  }
});
