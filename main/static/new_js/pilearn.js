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
  }
}
