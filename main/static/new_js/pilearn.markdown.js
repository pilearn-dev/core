PiJS.extend("markdown", {
  /*
   * PiJS.md.compile
   * ------
   *
   * Transforms a markdown text to html.
   * Complex and long approach (compilation).
   */
  compile: function(text) {

  },
  /*
   * PiJS.md.parse
   * ------
   *
   * Transforms a markdown text to html.
   * Simple and fast approach (regex).
   */
  parse: function(text, no_sanitize) {
    text = text.replace(/!\[(.*?)\]\((.*?)\)/g, "</p><img src=\"$2\" alt=\"$1\"><p>");
    text = PiJS.md.parse(text, true);
    text = text.replace(/\n\-\-\-+\n\n/g, "</p><hr><p>");
    text = text.replace(/(?:^|\n)###### (.*)/g, "</p><h6>$1</h6><p>");
    text = text.replace(/(?:^|\n)##### (.*)/g, "</p><h5>$1</h5><p>");
    text = text.replace(/(?:^|\n)#### (.*)/g, "</p><h4>$1</h4><p>");
    text = text.replace(/(?:^|\n)### (.*)/g, "</p><h3>$1</h3><p>");
    text = text.replace(/(?:^|\n)## (.*)/g, "</p><h2>$1</h2><p>");
    text = text.replace(/(?:^|\n)# (.*)/g, "</p><h1>$1</h1><p>");

    text = text.replace(/(?:^|\n)> (.*)/g, "</p><blockquote><p>$1</p></blockquote><p>");
    text = text.replace(/<\/blockquote><p><\/p><blockquote>/g, "");

    text = text.replace(/(?:^|\n)    (.*)/g, "</p><pre><code>$1</code></pre><p>");
    text = text.replace(/<\/code><\/pre><p><\/p><pre><code>/g, "\n");


    text = text.replace(/\[\[ language: ([a-zA-Z0-9 _.#+-]*?) \]\]\n\[\[ framework: ([a-zA-Z0-9 _.#+-]*?) \]\]<\/p><pre>/g, "<pre data-lang=\"$1\" data-framework=\"$2\">");
    text = text.replace(/\[\[ framework: ([a-zA-Z0-9 _.#+-]*?) \]\]<\/p><pre>/g, "<pre data-framework=\"$1\">");
    text = text.replace(/\[\[ language: ([a-zA-Z0-9 _.#+-]*?) \]\]<\/p><pre>/g, "<pre data-lang=\"$1\">");

    text = text.replace(/(?:^|\n)- (.*)/g, "</p><ul><li>$1</li></ul><p>");
    text = text.replace(/<\/ul><p><\/p><ul>/g, "");

    text = text.replace(/\n\n/g, "</p><p>");
    text = text.replace(/  \n/g, "<br>");
    text ="<p>" + text + "</p>"
    text = text.replace(/<p>[ \n]*<\/p>/g, "");
    if(!no_sanitize) {
      text = this.sanitize(text);
    }
    return text;
  },
  sanitize: function(html) {
    WHITELIST = [
      /\/?strong/,
      /\/?em/,
      /\/?code/,
      /\/a/, /a\s+href\s*=\s*\".+?\"/,
      /h(1|2|3)/,
      /p/,
      /hr/,
      /br/,
      /img\s+src\s*=\s*\".+?\"(\s+alt\s*=\s*\".*?\")?/,
      /\/?blockquote/,
      /\/pre/, /pre(\s+data-lang\s*=\s*\".+?\")?(\s+data-framework\s*=\s*\".+?\")?/,
      /\/?ul/,
      /\/?li/,
    ];
    html = html.replace(/<code>((?:.|\n)*?)<\/code>/g, function(all, first) {
      first = first.replace(/</g, "&lt;");
      first = first.replace(/>/g, "&gt;");
      first = first.replace(/"/g, "&quot;");
      return "<code>"+first+"</code>"
    })
    return html.replace(/\<(.*?)\>/g, function(all, first) {
      for (expr of WHITELIST) {
        if(first.match(expr)) {
          return "<"+first+">";
        }
      }
      return "";
    })
  }
})


PiJS.extend("md", {
  /*
   * PiJS.md.compile
   * ------
   *
   * Transforms a markdown text to html.
   * Complex and long approach (compilation).
   */
  compile: function(text) {

  },
  /*
   * PiJS.md.parse
   * ------
   *
   * Transforms a markdown text to html.
   * Simple and fast approach (regex).
   */
  parse: function(text, no_sanitize) {
    WHITELIST = [""]
    text = text.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.+?)\*/g, "<em>$1</em>");
    text = text.replace(/(\`+)(.*?)\1/g, "<code>$2</code>");
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, "<a href=\"$2\">$1</a>");
    text = text.replace(/\/t\/([a-z]+)/g, "<a href=\"/t/$1\">/t/$1</a>");
    if(!no_sanitize) {
      text = this.sanitize(text);
    }
      return text;
  },
  sanitize: function(html) {
    WHITELIST = [/\/?strong/, /\/?em/, /\/?code/, /\/a/, /a\s+href\s*=\s*\".+?\"/];
    html = html.replace(/<code>((?:.|\n)*?)<\/code>/g, function(all, first) {
      first = first.replace(/</g, "&lt;");
      first = first.replace(/>/g, "&gt;");
      first = first.replace(/"/g, "&quot;");
      return "<code>"+first+"</code>"
    })
    return html.replace(/\<(.*?)\>/g, function(all, first) {
      for (expr of WHITELIST) {
        if(first.match(expr)) {
          return "<"+first+">";
        }
      }
      return "";
    })
  }
})
