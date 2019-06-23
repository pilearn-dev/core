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
      dialog.css("top", (3*15 + window.scrollY)+"px");
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
    },
    resetposition: function(dialog) {
      dialog.css("top", (3*15 + window.scrollY)+"px");
    }
  },
  warnbox: {
    _generate: function(cls, msg, parent, html) {
      parent = parent || false;
      dialog = $("<div class='_warnbox _warnbox-"+cls+" _warnbox-xed'>");
      if(parent) dialog.addClass("mt2 ml2");
      if(html)
        dialog.append($("<div>").html(msg));
      else
        dialog.append($("<p>").text(msg));
      dialog.append($("<button class='_warnbox-xed'>&times;</button>").click(function() { dialog.remove() }));
      (parent || $("body")).append(dialog);
    },
    error: function(msg, parent, html) {
      PiJS.warnbox._generate("danger", msg, parent, html)
    },
    warning: function(msg, parent, html) {
      PiJS.warnbox._generate("warning", msg, parent, html)
    },
    success: function(msg, parent, html) {
      PiJS.warnbox._generate("success", msg, parent, html)
    },
    info: function(msg, parent, html) {
      PiJS.warnbox._generate("info", msg, parent, html)
    }
  }
}

// STANDARD LIBRARY
$(window).on("load", function() {
  $("[data-toggle]").on("click", function() {
    $this = $(this);
    $el = $($this.attr("data-toggle"));

    if($this.attr("data-toggle-class"))
      $el.toggleClass($this.attr("data-toggle-class"));
    else
      $el.toggle();

    if($this.attr("data-toggle-self-class"))
      $this.toggleClass($this.attr("data-toggle-self-class"));
  })
});
