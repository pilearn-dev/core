function addTagInput(query) {
    el = document.querySelector(query);
    return new _TagInput(el);
}

var _TagInput = function (el) {
    this.el = el;
    this.tagHolder = el.querySelector("[data-id='tag-holder']");
    this.tagInput = el.querySelector("[data-id='tag-input']");
    this.tags = [];
    this.bannedTags = [];
    self = this;
    this.tagInput.addEventListener("keyup", this._onKeyPress)
    this.tagInput.oldValue = "";
    this.getExtraClass = function (tag) { return null; }
    this.mayBeSet = function (tag) { return true; }
    this.requirementMet = function (tag) { return true; }
    this.sync = function (tags) { }
    this._update(true)
}
_TagInput.prototype._update = function (iFU) {
    while (this.tagHolder.lastChild) {
        this.tagHolder.removeChild(this.tagHolder.lastChild);
    }
    for (var i = 0; i < this.tags.length; i++) {
        _ = document.createElement("a");
        x = this.tags[i];
        self = this;
        _.innerText = x;
        _.classList.add("tag");
        _.onclick = function () {
          self.tags = self.tags.slice(0, self.tags.indexOf(this.innerText)).concat(self.tags.slice(self.tags.indexOf(this.innerText)+1, self.tags.length))
          self._update()
        }
        extraClass = this.getExtraClass(x);
        if (extraClass != null) {
            _.classList.add(extraClass);
        }
        _.classList.add("no-break");
        this.tagHolder.appendChild(_)
    }
    if(iFU !== true) {
      this.tagInput.focus();
    }
    this.sync(this.tags)
}
_TagInput.prototype._onKeyPress = function (e) {
    key = e.keyCode || e.which;
    if (key == 13) {
        if (self.tags.length == 5) {
            alert("Du kannst nicht mehr als 5 Tags hinzufügen")
        } else if (self.tags.indexOf(this.value) != -1) {
            alert("Du kannst ein Tag nur einmal hinzufügen.");
            this.value = "";
            this.oldValue = "";
        } else if (!self.requirementMet(this.value)) {
            alert("Dieses Tag ist nicht gültig.");
        } else if (!self.mayBeSet(this.value)) {
            alert("Dieses Tag darfst du nicht setzen.");
        } else {
            self.tags.push(this.value)
            this.value = "";
            this.oldValue = "";
            self._update();
        }
        e.preventDefault();
    }
    this.oldValue = this.value;
}
