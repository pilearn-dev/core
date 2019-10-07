var RespectableReorder = function(qs) {
  this.el = $(qs);
  this.data = [];
}
RespectableReorder.prototype.loadStructure = function(data) { this.data = data; }

RespectableReorder.prototype.init = function() {
  this._update();
}

RespectableReorder.prototype._update = function() {
  this.el.html("");

  for (var i = 0; i < this.data.length; i++) {
    item = this.data[i]
    this.__createViewItem(item, i, false, this.data)

    if (item.subitems)
      for (var si = 0; si < item.subitems.length; si++) {
        subitem = item.subitems[si]
        this.__createViewItem(subitem, si, i, item.subitems)
      }
  }
}


RespectableReorder.prototype.__createViewItem = function(item, id, is_subordinate, data) {
  self = this;
  container = $("<div class='_card m0 colbox-fill'>");
  if(is_subordinate === false)
    container.append($("<div class='p3 fs-base3 _card-header'>").html(item.title));
  else
    container.append($("<div class='p3 fs-base3 _card-content'>").html(item.title));

  if(!item.availible)
    container.addClass("_card-danger");

  if(is_subordinate === false)
    wrapper = $("<div class='m1 mx8 m1__sm grid'>");
  else
    wrapper = $("<div class='m1 mx8 m1__sm grid pl6 pr2'>");

  btn_left_container = $("<div class='colbox50 fs-caption p0 m0'>");
  btn_left_flex_container = $("<div class='d-f -c ta-c mt0'>");
  btn_left_container.append(btn_left_flex_container);

  btn_right_container = $("<div class='colbox50 fs-caption p0 m0'>");
  btn_right_flex_container = $("<div class='d-f -c ta-c mt0'>");
  btn_right_container.append(btn_right_flex_container);

  up_btn = $('<button class="_btn _btn-white _btn-icononly _btn-xs">' +
               '<svg class="_btn-icon" width="1e0.4" height="1e0.4" viewbox="0 0 48 48">' +
                  '<path d="M24,12 l16,24 l-32,0 z" fill="transparent" stroke-width="3" />' +
               '</svg>' +
             '</button>');
  up_btn.on("click", function() { self.___moveItem(data, id, -1); self._update() });
  up_btn.attr("title", "Dieses nach oben verschieben.");

  down_btn = $('<button class="_btn _btn-white _btn-icononly _btn-xs">' +
                   '<svg class="_btn-icon" width="0.4em" height="0.4em" viewbox="0 0 48 48">' +
                      '<path d="M8,12 l32,0 l-16,24 z" fill="transparent" stroke-width="3" />' +
                   '</svg>' +
                 '</button>');
  down_btn.on("click", function() { self.___moveItem(data, id, 1); self._update() });
  down_btn.attr("title", "Dieses Element nach unten verschieben.");

  lr_btn = $('<button class="_btn _btn-white _btn-icononly _btn-xs">' +
                   '<svg class="_btn-icon col--primary" width="0.4em" height="0.4em" viewbox="0 0 48 48">' +
                   ((is_subordinate===false) ?
                      '<path d="M32,12 l0,32 l-24,-16 z" fill="transparent" stroke-width="3" />' :
                      '<path d="M8,12 l0,32 l24,-16 z" fill="transparent" stroke-width="3" />') +
                   '</svg>' +
                 '</button>');
  lr_btn.on("click", function() { self.___toggleIndentation(data, id, is_subordinate); self._update() });
  lr_btn.attr("title", "Dieses Element einrücken.");

  if(id != 0)
      btn_left_flex_container.append(up_btn);
  else
      btn_left_flex_container.append(up_btn.attr("disabled", "disabled").attr("title", null));

  if(id < data.length - 1)
      btn_left_flex_container.append(down_btn);
  else
      btn_left_flex_container.append(down_btn.attr("disabled", "disabled").attr("title", null));

  if (id != 0 || is_subordinate !== false)
      btn_right_flex_container.append(lr_btn);
  else
      btn_right_flex_container.append(lr_btn.attr("disabled", "disabled").attr("title", null));

  wrapper.append(btn_left_container);
  wrapper.append(container);
  wrapper.append(btn_right_container);

  this.el.append(wrapper);
}

RespectableReorder.prototype.___moveItem = function(data, id, dir) {
  result = id + dir;
  if(result < 0 || result >= data.length) return;
  temp = data[id];
  data[id] = data[result];
  data[result] = temp;
}
RespectableReorder.prototype.___toggleIndentation = function(data, id, parid) {
  if(parid === false) {
      xitem = data[id];

      select = [xitem];
      select = select.concat(xitem.subitems);
      select[0].subitems=null;

      data[id-1].subitems = data[id-1].subitems.concat(select);
      x = data.splice(id, 1);
  } else {
      subselect = data.splice(id);
      new_subitems = subselect.splice(1);
      subselect = subselect[0];
      subselect.subitems = new_subitems;
      this.data.splice(parid+1, 0, subselect);
  }
}
