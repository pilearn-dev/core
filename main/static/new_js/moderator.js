PiJS.route(/^\/user\/-?[0-9]/, function() {
  $(".js--mod-user-ops").click(function() {
    ud = location.href.match(/\/user\/(-?[0-9]+)\/(.*?)(\/|$)/)
    user_id = ud[1];
    PiJS.dialog.fromURL("/tools/user/"+user_id+"/dialog", true);
    return false;
  })
});
