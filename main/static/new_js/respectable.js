var RespectableEditor = function(qs) {
  this.el = $(qs);
  this.model = {};
  this.customEditors = {};
  this.data = [];
  this.mode = "view";
  this.editing_id = null;
}
RespectableEditor.prototype.loadModel = function(model) { this.model = model; }
RespectableEditor.prototype.loadContent = function(data) { this.data = data; }
RespectableEditor.prototype.loadCustomEditor = function(name, obj) { this.customEditors[name] = obj; }

RespectableEditor.prototype.init = function() {
  this._update();
}

RespectableEditor.prototype._update = function() {
  this.el.html("");

  for (var i = 0; i < this.data.length; i++) {
    item = this.data[i]
    if(this.mode == "view")
      this.__createViewItem(item, i)
    else if(this.mode == "edit" && i != this.editing_id)
      this.__createViewItem(item, i, true)
    else if(this.mode == "edit" && i == this.editing_id)
      this.__createEditorItem(item, i)
  }

  if(this.mode == "view") {
    self = this;
    btn_grid = $("<div class='grid bg--primary-lll p4 py2__sm'>");
    btn_inner_grid = $("<div class='grid'>");

    chooser_div = $("<div class='p3 py0__sm'>");
    chooser = $("<select class='form fs-base3' data-respectable-newselect>");

    for (var i = 0; i < Object.keys(this.model).length; i++) {
      key = Object.keys(this.model)[i];
      value = this.model[key];
      chooser.append($("<option>").text(value.label).attr("value", key))
    }


    chooser_div.append(chooser);

    btn_div = $("<div class='py3 py0__sm'>");
    btn = $("<button class='_btn _btn--primary _btn-xl'>Hinzufügen</button>");
    btn.on("click", function() {
      self.__showNewItemMenu();
    })
    btn_div.append(btn);

    btn_inner_grid.append(chooser_div);
    btn_inner_grid.append(btn_div);
    btn_grid.append(btn_inner_grid);

    this.el.append(btn_grid);
  }
}


RespectableEditor.prototype.__createViewItem = function(item, id, no_controls) {
  model = this.model[item.type];
  self = this;
  container = $("<div class='_card colbox-fill'>");
  container.append($("<div class='p4 _card-content'>").html(model.getPreview(item)))

  if(!no_controls) {
    self = this;
    wrapper = $("<div class='m2 mx8 m1__sm grid'>");

    btn_left_container = $("<div class='colbox50 fs-caption p2'>");
    btn_left_flex_container = $("<div class='d-f -c ta-c mt0'>");
    btn_left_container.append(btn_left_flex_container);

    btn_right_container = $("<div class='colbox50 fs-caption p2'>");
    btn_right_flex_container = $("<div class='d-f -c ta-c mt0'>");
    btn_right_container.append(btn_right_flex_container);

    up_btn = $('<button class="_btn _btn-white _btn-icononly _btn-xs">' +
               '<svg class="_btn-icon" width="1e0.4" height="1e0.4" viewbox="0 0 48 48">' +
                  '<path d="M24,12 l16,24 l-32,0 z" fill="transparent" stroke-width="3" />' +
               '</svg>' +
             '</button>');
    up_btn.on("click", function() { self.___moveItem(id, -1); self._update() });
    up_btn.attr("title", "Dieses Element vom Typ " + model.label + " nach oben verschieben.");

    down_btn = $('<button class="_btn _btn-white _btn-icononly _btn-xs">' +
                   '<svg class="_btn-icon" width="0.4em" height="0.4em" viewbox="0 0 48 48">' +
                      '<path d="M8,12 l32,0 l-16,24 z" fill="transparent" stroke-width="3" />' +
                   '</svg>' +
                 '</button>');
    down_btn.on("click", function() { self.___moveItem(id, 1); self._update() });
    down_btn.attr("title", "Dieses Element vom Typ " + model.label + " nach unten verschieben.");

    del_btn = $('<button class="_btn _btn-danger _btn-icononly _btn-xs">' +
                   '<svg class="_btn-icon col-danger-dd" width="0.4em" height="0.4em" viewbox="0 0 48 48">' +
                      '<path d="M12,12 L36,36 M12,36 L36,12" fill="transparent" stroke-width="3" />' +
                   '</svg>' +
                 '</button>');
    del_btn.on("click", function() { self.___deleteItem(id); self._update() });
    del_btn.attr("title", "Dieses Element vom Typ " + model.label + " löschen.");

    edit_btn = $('<button class="_btn _btn--primary _btn-icononly _btn-xs">' +
                   '<svg class="_btn-icon col--primary-dd" width="0.4em" height="0.4em" viewbox="0 0 48 48">' +
                      '<path d="M6,32 v8 h8 L42,12 l-8,-8 z M36,18 l-8,-8" fill="transparent" stroke-width="3" />' +
                      '<path d="M6,32 v8 h8 z" />' +
                   '</svg>' +
                 '</button>');
    edit_btn.on("click", function() { self.editing_id = id; self.mode = "edit"; self._update(); });
    edit_btn.attr("title", "Dieses Element vom Typ " + model.label + " bearbeiten.");

    if(id != 0)
      btn_left_flex_container.append(up_btn);
    else
      btn_left_flex_container.append(up_btn.attr("disabled", "disabled").attr("title", null));

    if(id < this.data.length - 1)
      btn_left_flex_container.append(down_btn);
    else
      btn_left_flex_container.append(down_btn.attr("disabled", "disabled").attr("title", null));

    if (model.is_editable)
      btn_right_flex_container.append(edit_btn);
    btn_right_flex_container.append(del_btn);


    wrapper.append(btn_left_container);
    wrapper.append(container);
    wrapper.append(btn_right_container);
    this.el.append(wrapper);
  } else {
    wrapper = $("<div class='m2 mx8 m1__sm grid'>");
    btn_left_container = $("<div class='colbox50 hide__sm p2'>");
    wrapper.append(btn_left_container);

    wrapper.append(container);

    btn_right_container = $("<div class='colbox50 hide__sm p2'>");
    wrapper.append(btn_right_container);

    this.el.append(wrapper);
  }
}

RespectableEditor.prototype.__createEditorItem = function(item, id) {
  model = this.model[item.type];
  self = this;

  container = $("<div class='colbox-fill _card s2'>");

  title = $("<div class='_card-title _card-subtitle'>").text(model.label + " bearbeiten");
  container.append(title);

  container.append($("<div class='p4 _card-content'>").append(self.___buildEditor(item.data, model.getEditor(item))));


  footer = $("<div class='_card-footer'>");
  footer.append($("<button class='_btn _btn--primary'>Speichern</button>").on("click", function() {
    self.___saveItem(id);
    self._update();
  }));
  footer.append($("<button class='_btn _btn--primary'>Abbrechen</button>").on("click", function() {
    self.editing_id = null;
    self.mode = "view";
    self._update();
  }));
  container.append(footer);

  wrapper = $("<div class='m4 mx2 m1__sm grid'>");
  btn_left_container = $("<div class='colbox50 hide__sm p2'>");
  wrapper.append(btn_left_container);

  wrapper.append(container);

  btn_right_container = $("<div class='colbox50 hide__sm p2'>");
  wrapper.append(btn_right_container);

  this.el.append(wrapper);
}


RespectableEditor.prototype.___deleteItem = function(id) {
  this.data.splice(id, 1);
}

RespectableEditor.prototype.___moveItem = function(id, dir) {
  result = id + dir;
  if(result < 0 || result >= this.data.length) return;
  temp = this.data[id];
  this.data[id] = this.data[result];
  this.data[result] = temp;
}

RespectableEditor.prototype.___buildEditor = function(item, data) {
  editor_container = $("<div>");

  for (var i = 0; i < data[0].length; i++) {
    field = data[0][i];

    value = data[1][field.name] || item[field.name];

    element_container = $("<div class='p1'>").attr("data-respectable-field", field.name);
    element_label = $("<label class='form'>").text(field.label);
    element_container.append(element_label);
    element_container.append(this.____buildField(field, value));


    editor_container.append(element_container);
  }

  window.setTimeout(function() { PiJS.editor.init(); }, 40);

  return editor_container;
}

RespectableEditor.prototype.____buildField = function(field, value) {

  if(field.type == "input") {
    return $("<input class='form'>").val(value);
  } else if(field.type == "text") {
    return $("<textarea class='form'>").val(value);
  } else if(field.type == "number") {
    return $("<input class='form' type='number'>").val(value);
  } else if(field.type == "markdown") {
    editor_wrapper = $("<div class='js--editor py2 js--editor:preview'>");
    editor_textarea = $("<textarea class='form form-large js--editor-textarea'>").val(value);
    editor_preview = $("<div class='p2 js--editor-preview hr-original'>");

    editor_wrapper.append(editor_textarea).append(editor_preview);

    return editor_wrapper;

  } else if(field.type == "select") {
    select = $("<select class='form'>");
    for (var i = 0; i < Object.keys(field.options).length; i++) {
      key = Object.keys(field.options)[i];
      key_value = field.options[key]
      option = $("<option>").text(key_value).attr("value", key);
      if(key == value) {
        option.attr("selected", "selected");
      }
      select.append(option);
    }
    return select;
  } else if(field.type == "image") {
    editor_wrapper = $("<div class='py2'>");
    editor_dialog = $("<iframe src='/upload/dialog' class='iframe-embed'>");
    editor_input = $("<input class='form' placeholder='Pfad zum Bild'>").val(value);

    editor_wrapper.append(editor_dialog).append(editor_input);

    return editor_wrapper;

  } else if(field.type == "custom") {
    return this.customEditors[field.customId].create(field, value);
  }

}


RespectableEditor.prototype.___saveItem = function(id) {
  item = this.data[id];
  model = this.model[item.type];
  data = model.getEditor(item);
  resolution = {};


  for (var i = 0; i < data[0].length; i++) {
    field = data[0][i];


    element_container = $("[data-respectable-field='" + field.name + "']");

    if(field.type == "input" || field.type == "image" || field.type == "number") {
      resolution[field.name] = element_container.find("input").val()
    } else if(field.type == "text" || field.type == "markdown") {
      resolution[field.name] = element_container.find("textarea").val()
    } else if(field.type == "select") {
      resolution[field.name] = element_container.find("select").val()
    } else if(field.type == "custom") {
      resolution[field.name] = this.customEditors[field.customId].parse(field, element_container);
    }
  }

  this.data[id].data = model.getEditedContent(resolution);
  this.editing_id = null;
  this.mode = "view";
}


RespectableEditor.prototype.__showNewItemMenu = function() {
  new_item = $("[data-respectable-newselect]").val();

  new_item_code = { type: new_item, data: JSON.parse(JSON.stringify(this.model[new_item].empty)) };
  this.data.push(new_item_code);
  this._update();
}
