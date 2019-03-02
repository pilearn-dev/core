var PiJS__Editor = function(editor) {
  this.editor = editor;
};
PiJS__Editor.prototype.init = function() {
  this.input = this.editor.children(".js--editor-textarea");

  if(this.editor.hasClass("js--editor:preview")) {

    this.preview = this.editor.children(".js--editor-preview");

    if(this.editor.hasClass("js--editor:inline")) {
      this.preview.html(PiJS.md.parse(this.input.val()));

      this.input.on("input", function() {
        this.preview.html(PiJS.md.parse(this.input.val()));
      }.bind(this))
      this.input.on("keypress", function() {
        this.preview.html(PiJS.md.parse(this.input.val()));
      }.bind(this))
      this.input.on("change", function() {
        this.preview.html(PiJS.md.parse(this.input.val()));
      }.bind(this))
    } else {
      this.preview.html(PiJS.markdown.parse(this.input.val()));

      this.input.on("input", function() {
        this.preview.html(PiJS.markdown.parse(this.input.val()));
      }.bind(this))
      this.input.on("keypress", function() {
        this.preview.html(PiJS.markdown.parse(this.input.val()));
      }.bind(this))
      this.input.on("change", function() {
        this.preview.html(PiJS.markdown.parse(this.input.val()));
      }.bind(this))
    }
  }
  if(!this.editor.hasClass("js--editor:nobar")) {
    this.editor.find("[data-editor-insert]").on("click", this.insert.bind(this))
  }
};
PiJS__Editor.prototype.insert = function(event) {
  target = $(event.target);
  switch (target.attr("data-editor-insert")) {
    case "bold":
      this._surround_selection("**","**");
      break;
    case "italic":
      this._surround_selection("*","*");
      break;
    case "inlinecode":
      this._surround_selection("`","`");
      break;
    case "link":
      this._intelligent_link("[:txt:](:lnk:)");
      break;
    case "image":
      this._intelligent_link("![:txt:](:lnk:)");
      break;
    case "h1":
      this._insert_at_line_start("# ");
      break;
    case "h2":
      this._insert_at_line_start("## ");
      break;
    case "h3":
      this._insert_at_line_start("### ");
      break;
    case "blockcode":
      this._insert_at_line_start("    ");
      break;
    case "quote":
      this._insert_at_line_start("> ");
      break;
    case "chars":
      this._char_dialog();
      break;
  }
}
PiJS__Editor.prototype._surround_selection = function(before, after) {
  var   start= this.input[0].selectionStart;
  var     end= this.input[0].selectionEnd;
  var  presel= this.input.val().substring(0, start);
  var     sel= this.input.val().substring(start, end);
  var postsel= this.input.val().substring(end, this.input.val().length);

  if(sel.substring(0, before.length) == before && sel.substring(sel.length - after.length, sel.length) == after) {
    sel = sel.substring(before.length, sel.length - after.length);
  } else if(presel.substring(presel.length - before.length, presel.length) == before && postsel.substring(0, after.length) == after) {
    presel = presel.substring(0, presel.length - before.length);
    postsel = postsel.substring(after.length, postsel.length);
    start -= before.length;
    end -= before.length + after.length;
  } else {
    sel = before + sel + after;
  }

  this.input.val(presel + sel + postsel);
  this.input.trigger("keypress");
  this.input[0].selectionStart = start;
  this.input[0].selectionEnd = start+sel.length;
  this.input[0].focus();
}
PiJS__Editor.prototype._intelligent_link = function(pattern) {
  var   start= this.input[0].selectionStart;
  var     end= this.input[0].selectionEnd;
  var  presel= this.input.val().substring(0, start);
  var     sel= this.input.val().substring(start, end);
  var postsel= this.input.val().substring(end, this.input.val().length);

  if(sel.match(/^(http|ftp)s?:\/\/[a-zA-Z0-9]([a-zA-Z0-9_.-]+[a-zA-Z0-9])?\.[a-z]{3,6}[a-zA-Z0-9._~#\?\/\+=_]*/)) {
    pattern = pattern.replace(":lnk:", sel);
    sel = pattern.replace(":txt:", "Text einfügen");
  } else {
    sel = pattern.replace(":txt:", sel);
    sel = sel.replace(":lnk:", "#ziel");
  }

  this.input.val(presel + sel + postsel);
  this.input.trigger("keypress");
  this.input[0].selectionStart = start;
  this.input[0].selectionEnd = start+sel.length;
  this.input[0].focus();
}

PiJS__Editor.prototype._insert_at_line_start = function(before) {
  var   start= this.input[0].selectionStart;
  var     end= this.input[0].selectionEnd;
  var  presel= this.input.val().substring(0, start);
  var     sel= this.input.val().substring(start, end);
  var postsel= this.input.val().substring(end, this.input.val().length);


  new_start = presel.lastIndexOf("\n") + 1;

  sel = this.input.val().substring(new_start, end);
  presel = this.input.val().substring(0, new_start);

  sel = sel.split("\n");

  is_reversal = true;

  for (line of sel) {
    if(line.substring(0, before.length) != before) {
      is_reversal = false;
    }
  }

  new_sel = [];
  dl = 0
  if(is_reversal) {
    for (line of sel) {
      new_sel.push(line.substring(before.length, line.length))
      dl -= before.length
    }
  } else {
    for (line of sel) {
      new_sel.push(before + line);
      dl += before.length
    }
  }

  sel = new_sel.join("\n");

  this.input.val(presel + sel + postsel);
  this.input.trigger("keypress");
  this.input[0].selectionStart = end + dl;
  this.input[0].selectionEnd = end + dl;
  this.input[0].focus();
}
PiJS__Editor.prototype._char_dialog = function() {
  dialog = $("<div>").addClass(PiJS.editor.styles.dialog);
  dialog.append(
    $("<h3>").addClass(PiJS.editor.styles.dialogHeading).text("Zeichen einfügen"));


  function inserter(e) {
    var   start= this.input[0].selectionStart;
    var     end= this.input[0].selectionEnd;
    var  presel= this.input.val().substring(0, start);
    var     sel= this.input.val().substring(start, end);
    var postsel= this.input.val().substring(end, this.input.val().length);

    sel = e.target.innerText;

    dialog.remove();

    this.input.val(presel + sel + postsel);
    this.input.trigger("keypress");
    this.input[0].selectionStart = end + dl;
    this.input[0].selectionEnd = end + dl;
    this.input[0].focus();

  }
  charlist = $("<div>").addClass(PiJS.editor.styles.btnlist_chars);

  for (var i = 0; i < PiJS.editor.chars.length; i++) {
    charlist.append(
      $("<button>")
      .addClass(PiJS.editor.styles.button_chars)
        .text(PiJS.editor.chars[i])
        .on("click", inserter.bind(this))
    );
  }


  dialog.append(charlist);

  dialog.append(
    $("<button>")
    .addClass(PiJS.editor.styles.button)
    .text("Abbrechen")
    .on("click", function(){dialog.remove()})
  );

  this.editor.prepend(dialog);
}




PiJS.extend("editor", {
  styles: {
    button: "_btn _btn-dark _btn-lighter",
    btnlist: "_btnlist _btnlist-close",
    toolbar: "horizontal-list",
    dialog: "_floatbox _dialog-medium m0 p2",
    dialogHeading: "fs-base3 m0 ml2 mt2",
    button_chars: "_btn _btn-dark _btn-outline _btn-sm",
    btnlist_chars: "_btnlist"
  },
  init: function() {
    $(".js--editor").each(function(i,editor) {
      editor = $(editor);


      if(!editor.hasClass("js--editor:nobar")) {
        horizontal_list = $("<div>").addClass(PiJS.editor.styles.toolbar);

        item_btnlist = $("<div>").addClass(PiJS.editor.styles.btnlist);
        item_btnlist.append(
          $("<button>").text("B").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "bold").attr("title", "Den ausgewählten Text fett formattieren"));
        item_btnlist.append(
          $("<button>").text("I").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "italic").attr("title", "Den ausgewählten Text kursiv formattieren"));
        item_btnlist.append(
          $("<button>").text("Link").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "link").attr("title", "Den ausgewählten Text in einen Link umwandeln"));
        item_btnlist.append(
          $("<button>").text("Bild").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "image").attr("title", "Ein Bild an der aktuellen Position einfügen"));
        item_btnlist.append(
          $("<button>").text("Code").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "inlinecode").attr("title", "Den ausgewählten Text als Quellcode formattieren"));
        item_btnlist.append(
          $("<button>").text("Ω").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "chars").attr("title", "Ein Sonderzeichen einfügen"));

        horizontal_list.append(item_btnlist);

      }

      if(!editor.hasClass("js--editor:inline") && !editor.hasClass("js--editor:nobar")) {

        line_btnlist = $("<div>").addClass(PiJS.editor.styles.btnlist);
        line_btnlist.append(
          $("<button>").text("H1").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "h1").attr("title", "Die ausgewählte Zeile zu einer Überschrift 1. Stufe konvertieren"));
        line_btnlist.append(
          $("<button>").text("H2").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "h2").attr("title", "Die ausgewählte Zeile zu einer Überschrift 2. Stufe konvertieren"));
        line_btnlist.append(
          $("<button>").text("H3").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "h3").attr("title", "Die ausgewählte Zeile zu einer Überschrift 3. Stufe konvertieren"));
        line_btnlist.append(
          $("<button>").text("\"...\"").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "quote").attr("title", "Den ausgewählten Text als Zitat kennzeichen"));
        line_btnlist.append(
          $("<button>").text("</>").addClass(PiJS.editor.styles.button).attr("data-editor-insert", "blockcode").attr("title", "Den ausgewählten Text als Quellcode-Block kennzeichen"));

        horizontal_list.append(line_btnlist);
      }

      if(!editor.hasClass("js--editor:nobar")) {
        editor.prepend(horizontal_list);
      }

      (new PiJS__Editor(editor)).init();
    });
  },
  "chars": [
    "±", "×", "·", "÷", "¬", "²", "³", "Ø", "¼", "½", "¾", "∛", "∜", "√",
    "„", "“", "❝", "❞", "‟", "”", "«", "»", "—", "–",
    "¶", "§", "©", "Æ", "�", "★",
    "←", "↑", "→", "↓", "↔", "↕", "↖", "↗", "↘", "↙", "▲", "▼", "◀", "▶"
  ]
});
