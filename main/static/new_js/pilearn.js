var PiJS = {
  extend: function(name, object) {
    PiJS[name] = object
  },
  qs: function(key) {
    key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
    var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
    return match && decodeURIComponent(match[1].replace(/\+/g, " "));
  },
  d: {
    cl: function(x) {
      console.log(x)
      return x;
    }
  },
  regex: {
    // Escapes a string for use in a regex. From MSDN
    escape: function(string){
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
  },
  route: function(route, cb) {
    if(location.pathname.match(route)) cb();
  },
  dialog: {
    _generate: function(html, bd) {
      bd = bd || false;
      dialog = $("<div class='_dialog'>");
      if(bd) dialog.addClass("_dialog-backdrop");
      dialog.append($("<a href='#!' class='_xbtn _dialog-xbtn'>&times</a>").click(function() { dialog.remove() }));
      dialog.append($(html));
      $("body").append(dialog);
    },
    fromURL: function(url, bd) {
      $.ajax({
        method: "POST",
        url: url,
        success: function( result ) {
          PiJS.dialog._generate(result, bd);
        }
      });
    }
  }
}
