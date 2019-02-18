function draw_reorder(reorder, data) {
    reorder.innerHTML = "";
    reorder.setAttribute("data-dnd-container", true);

    for (var i = 0; i < data.length; i++) {
        container = document.createElement("div");
        container.classList.add("reorder-item");
        container.setAttribute("data-dragable", true);
        container.setAttribute("data-dropable", true);
        container.setAttribute("data-id", data[i].id);

        title = document.createElement("span");
        title.innerText = data[i].title + " (" + data[i].id + ")";
        container.appendChild(title);

        indenter = document.createElement("a");
        indenter.innerText = "(aus-/einrücken)";
        indenter.container = container;
        indenter.addEventListener("click", function() {
          this.container.classList.toggle("indented");
        });
        container.appendChild(indenter);

        reorder.appendChild(container);
        for (var j = 0; j < data[i].subitems.length; j++) {
            container = document.createElement("div");
            container.classList.add("reorder-item");
            container.classList.add("indented");
            container.setAttribute("data-dragable", true);
            container.setAttribute("data-dropable", true);
            container.setAttribute("data-id", data[i].subitems[j].id);

            title = document.createElement("span");
            title.innerText = data[i].subitems[j].title + " (" + data[i].subitems[j].id + ")";
            container.appendChild(title);

            indenter = document.createElement("a");
            indenter.innerText = "(aus-/einrücken)";
            indenter.container = container;
            indenter.addEventListener("click", function() {
              this.container.classList.toggle("indented");
            });
            container.appendChild(indenter);

            reorder.appendChild(container);
        }
    }
}

window.addEventListener("load", function() {
    reorder = document.getElementById("reorder");
    data = REORDER_DATA;
    draw_reorder(reorder, data);

    function objHTML5DnD() {}
    objHTML5DnD.prototype.dragSrcEl = null, objHTML5DnD
        .prototype.parse = function(t) {
            "boolean" != typeof t && (t = !0), _this = this,
                all = document.querySelectorAll(
                    "[data-dnd-container]");
            for (var e = 0; e < all.length; e++) all[e]
                .classList.add("html5dnd-" + String(e) +
                    "-root"), _this._private__container_parse(
                    "html5dnd-" + String(e), t);
            s = document.createElement("style"), s.innerHTML =
                "[data-dragable] {cursor: move;} [data-dragable][draggable] {-moz-user-select: none;-khtml-user-select: none;-webkit-user-select: none;user-select: none;-khtml-user-drag: element;-webkit-user-drag: element;}",
                document.body.appendChild(s)
        }, objHTML5DnD.prototype.__makeDragable = function(t,
            e, a) {
            t.setAttribute("data-group", e + "-child"),
                _this = this, t.setAttribute("draggable", !
                    0), t.addEventListener("dragstart",
                    function(
                        t) {
                        var e = this.outerHTML;
                        this.classList.add("dragging"), _this
                            .dragSrcEl = this, t.dataTransfer
                            .effectAllowed = "move", t
                            .dataTransfer.setData("text/html",
                                e)
                    }, !1), t.addEventListener("dragend",
                    function(t) {
                        this.classList.remove("dragging"), x =
                            document.querySelectorAll("." +
                                e + " .drop-hover, ." + e +
                                " .dragging"), t.dataTransfer
                            .effectAllowed = "uninitialized"
                    }, !1)
        }, objHTML5DnD.prototype.__makeDropable = function(t,
            e, a) {
            t.setAttribute("data-group", e + "-child"),
                _this = this, t.addEventListener("drop",
                    function(t) {
                        if (t.stopPropagation && t
                            .stopPropagation(), classes =
                            accept = deny = "", _this
                            .dragSrcEl.hasAttribute(
                                "data-classes") && (classes =
                                _this.dragSrcEl.getAttribute(
                                    "data-classes")
                                .split(",")
                            ), this.hasAttribute(
                                "data-accept")) {
                            if (accept = this.getAttribute(
                                    "data-accept")
                                .split(","),
                                "" == classes) return;
                            for (var r = 0; r < accept
                                .length; r++)
                                if (!classes.includes(accept[
                                        r])) return
                        } else if (this.hasAttribute(
                                "data-deny") && (deny = this
                                .getAttribute("data-deny")
                                .split(","), "" != classes))
                            for (var r = 0; r < deny
                                .length; r++)
                                if (classes.includes(deny[r]))
                                    return;
                        return this.getAttribute(
                                "data-group") != _this
                            .dragSrcEl
                            .getAttribute("data-group") ? !1 :
                            (_this.dragSrcEl != this && (
                                    isDragable = this
                                    .hasAttribute(
                                        "data-dragable"),
                                    _this.dragSrcEl.parentNode.removeChild(_this.dragSrcEl),
                                    L = document.createElement("div"),
                                    L.innerHTML = t
                                        .dataTransfer.getData(
                                            "text/html"),
                                    (this.classList.contains("indented")?L.firstChild.classList.add("indented"):L.firstChild.classList.remove("indented")),
                                    La = L.firstChild.querySelector("a"),
                                    La.container=L.firstChild,
                                    (La.addEventListener("click", function() {
                                      this.container.classList.toggle("indented");
                                    })),
                                    this.parentNode.insertBefore(L.firstChild, this.nextSibling)),
                                x = document
                                .querySelectorAll(
                                    "." + e +
                                    " .drop-hover, ." + e +
                                    " .dragging"), _this
                                ._private__container_parse(e,
                                    a), !1)
                    }, !1), t.addEventListener("dragenter",
                    function(t) {
                        if (classes = accept = deny = "",
                            _this.dragSrcEl.hasAttribute(
                                "data-classes") && (classes =
                                _this.dragSrcEl.getAttribute(
                                    "data-classes")
                                .split(",")
                            ), this.hasAttribute(
                                "data-accept")) {
                            if (accept = this.getAttribute(
                                    "data-accept")
                                .split(","),
                                "" == classes) return;
                            for (var e = 0; e < accept
                                .length; e++)
                                if (!classes.includes(accept[
                                        e])) return
                        } else if (this.hasAttribute(
                                "data-deny") && (deny = this
                                .getAttribute("data-deny")
                                .split(","), "" != classes))
                            for (var e = 0; e < deny
                                .length; e++)
                                if (classes.includes(deny[e]))
                                    return;
                        this.getAttribute("data-group") ==
                            _this.dragSrcEl.getAttribute(
                                "data-group") && this
                            .classList.add("drop-hover")
                    }, !1), t.addEventListener("dragover",
                    function(t) {
                        return t.preventDefault && t
                            .preventDefault(), !1
                    }, !1), t.addEventListener("dragleave",
                    function(t) {
                        this.getAttribute("data-group") ==
                            _this.dragSrcEl.getAttribute(
                                "data-group") && this
                            .classList.remove("drop-hover")
                    }, !1)
        }, objHTML5DnD.prototype._private__container_parse =
        function(t, e) {
            _this = this, all_draggable = document
                .querySelectorAll("." + t +
                    "-root [data-dragable]");
            for (var a = 0; a < all_draggable.length; a++)
                all_draggable[a].classList.remove("dragging"),
                _this.__makeDragable(all_draggable[a], t,
                    e);
            all_dropable = document.querySelectorAll("." + t +
                "-root [data-dropable]");
            for (var a = 0; a < all_dropable.length; a++)
                all_dropable[a].classList.remove(
                    "drop-hover"), _this.__makeDropable(
                    all_dropable[a], t, e)
        };
    var HTML5DnD = new objHTML5DnD;

    function submitOrder() {
      $post("c/"+COURSE_ID+"/unit_reorder", getOrder('#reorder'), function (e) {
        window.location.href = "./start";
      });
    }
    window.submitOrder = submitOrder;
    HTML5DnD.parse();

    function getOrder(obj) {
        order = [];
        all = document.querySelectorAll(obj +
            " [data-dragable]");
        oc = 1;
        for (var i = 0; i < all.length; i++) {
            if (all[i].hasAttribute("data-id") && all[i]
                .getAttribute("data-id") != "") {
                if(all[i].classList.contains("indented")) {
                  ai = order[order.length-1];
                  ai.subitems.push({
                    "order": ai.subitems.length + 1,
                    "id": all[i].getAttribute("data-id"),
                  });
                  order[order.length-1] = ai;
                } else {
                  order.push({
                    "order": oc,
                    "id": all[i].getAttribute("data-id"),
                    "subitems": []
                  });
                  oc++;
                }
            }
        }
        return order;
    }

});
