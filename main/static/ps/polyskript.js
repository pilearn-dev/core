function generate_Card(content, mode, lib, id) {
  card = document.createElement("div");
  card.classList.add("box");

  card_title = document.createElement("div");
  card_title.classList.add("box-type");
  card_title.innerText = MODEL[content.type].label;
  card.appendChild(card_title);

  card.setAttribute("data-ps-id", id)

  card_preview = document.createElement("div");
  card_preview.classList.add("box-preview");
  if(mode == "view" || mode == "blank") {
    card_preview.appendChild(MODEL[content.type].getPreview(content));
  } else if(mode == "edit") {
    card_preview.appendChild(MODEL[content.type].getEditor(content));
  }
  card.appendChild(card_preview);
  card.classList.add("box-mode-"+mode);

  card_actions = document.createElement("div");
  card_actions.classList.add("box-actions");
  if(mode == "blank") {
   card_actions.innerHTML = "&nbsp;";
  } else if(mode == "view") {
    btn1 = document.createElement("button")
    btn1.classList.add("primary");
    btn1.onclick = lib.edit.bind(card);
    btn1.innerText = "Bearbeiten";
    if(!MODEL[content.type].is_editable) {
      btn1.setAttribute("disabled", "disabled")
    }
    card_actions.appendChild(btn1);

    btn2 = document.createElement("button")
    btn2.classList.add("secondary");
    btn2.onclick = lib.moveup.bind(card);
    btn2.innerText = "Nach oben";
    card_actions.appendChild(btn2);

    btn3 = document.createElement("button")
    btn3.classList.add("secondary");
    btn3.onclick = lib.movedown.bind(card);
    btn3.innerText = "Nach unten";
    card_actions.appendChild(btn3);

    btn4 = document.createElement("button")
    btn4.classList.add("dangerous");
    btn4.onclick = lib.delete.bind(card);
    btn4.innerText = "Löschen";
    card_actions.appendChild(btn4);
  } else if(mode == "edit") {
    btn1 = document.createElement("button")
    btn1.classList.add("primary");
    btn1.onclick = lib.save_edit.bind(card);
    btn1.innerText = "Speichern";
    card_actions.appendChild(btn1);

    btn2 = document.createElement("button")
    btn2.classList.add("secondary");
    btn2.onclick = lib.cancel_edit.bind(card);
    btn2.innerText = "Abbrechen";
    card_actions.appendChild(btn2);
  }
  card.appendChild(card_actions);

  return card;
}




var Polyskript = function (data) {
  this.data = data;
  this.in_edit_mode = null;
  this.in_view_mode = false;
  self = this;
  this._lib = {
    "edit": function() {
      id = parseInt(this.getAttribute("data-ps-id"));
      self.in_edit_mode = id;
      self._update()
    },
    "moveup": function() {
      id = parseInt(this.getAttribute("data-ps-id"));
      if(id != 0) {
        prv = self.data[id - 1];
        ths = self.data[id];
        self.data[id] = prv;
        self.data[id - 1] = ths;
      }
      self._update();
    },
    "movedown": function() {
      id = parseInt(this.getAttribute("data-ps-id"));
      if(id != self.data.length - 1) {
        prv = self.data[id + 1];
        ths = self.data[id];
        self.data[id] = prv;
        self.data[id + 1] = ths;
      }
      self._update();
    },
    "delete": function() {
      id = parseInt(this.getAttribute("data-ps-id"));
      self.data = self.data.slice(0, id).concat(self.data.slice(id+1, self.data.length));
      self._update()
    },
    "save_edit": function() {
      id = parseInt(this.getAttribute("data-ps-id"));
      self.data[id].data = MODEL[self.data[id].type].getEditedContent(this);
      self.in_edit_mode = null;
      self._update();
    },
    "cancel_edit": function() {
      self.in_edit_mode = null;
      self._update();
    },
    "new": function (e) {
      this.setAttribute("disabled", "disabled");
      el = document.createElement("ul");
      el.classList.add("append-element-list");
      keys = Object.keys(MODEL);
      for (var i = 0; i < keys.length; i++) {
        elel = document.createElement("li");
        k = keys[i];
        elel.innerText = MODEL[k].label;
        elel.setAttribute("data-ps-key", k)
        elel.onclick = self._lib.new_create;
        el.appendChild(elel);
      }
      elel = document.createElement("li");
      elel.innerHTML = "<em>Abbrechen</em>";
      elel.onclick = self._update.bind(self);
      el.appendChild(elel);
      document.querySelector("#polyskript-master .preview").appendChild(el);
    },
    "new_create": function () {
      key = this.getAttribute("data-ps-key");
      self.data.push({
        "type": key,
        "data": MODEL[key].empty
      })
      self._update()
    }
  }
}
Polyskript.prototype._update = function () {
  prev = document.querySelector("#polyskript-master .preview");
  prev.innerHTML = "";
  if(!this.in_view_mode) {
    prev.classList.remove("view-mode");
    for (var i = 0; i < this.data.length; i++) {
      if(this.in_edit_mode == i) {
        card = generate_Card(this.data[i], "edit", this._lib, i);
      } else if(this.in_edit_mode === null) {
        card = generate_Card(this.data[i], "view", this._lib, i);
      } else {
        card = generate_Card(this.data[i], "blank", this._lib, i);
      }
      prev.appendChild(card);
    }
    if(this.data.length == 0) {
      prev.innerHTML = "<p>Es gibt (noch) keine Elemente, füge Elemente durch Drücken auf <code>+</code> hinzu.</p>";
    }
    apbtnm = document.createElement("div");
    apbtnm.classList.add("append-button");
    apbtn = document.createElement("button");
    apbtn.innerText = "+";
    apbtn.onclick = this._lib.new;
    apbtnm.appendChild(apbtn);
    prev.appendChild(apbtnm);
  } else {
    for (var i = 0; i < this.data.length; i++) {
      prev.classList.add("view-mode");
      card = MODEL[this.data[i].type].getView(this.data[i]);
      prev.appendChild(card);
    }
  }
};
Polyskript.prototype.show = function () {
  this.in_edit_mode = null;
  this._update();
};
Polyskript.prototype.toggle_view = function () {
  this.in_view_mode = !this.in_view_mode;
  this._update();
};
Polyskript.prototype.to_view_mode = function () {
  this.in_view_mode = true;
  this._update();
};
Polyskript.prototype.to_edit_mode = function () {
  this.in_view_mode = false;
  this._update();
};
