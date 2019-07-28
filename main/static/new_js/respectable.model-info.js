function simple_md(text) {
    return PiJS.markdown.parse(text)
}

var MODEL = {
  "heading": {
    "label": "Überschrift (1. Ordnung)",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h1");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Text", name: "text", type: "input" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "subheading": {
    "label": "Überschrift (2. Ordnung)",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h2");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Text", name: "text", type: "input" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "subsubheading": {
    "label": "Überschrift (3. Ordnung)",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h3");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Text", name: "text", type: "input" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "text": {
    "label": "Text",
    "is_editable": true,
    "empty": {"text":"Text hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("div");
      el.innerHTML = simple_md(box.data.text)
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Inhalt", name: "text", type: "markdown" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "separator": {
    "label": "Trennlinie",
    "is_editable": false,
    "empty": {},
    "getPreview": function (box) {
      return document.createElement("hr");
    },
    "getEditor": null,
    "getEditedContent": null
  },
  "warnbox": {
    "label": "Warnung",
    "is_editable": true,
    "empty": {"text":"Warnung hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("div");
      el.classList.add("_alert", "_alert-warning");
      el.innerHTML = simple_md(box.data.text)
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Inhalt", name: "text", type: "markdown" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "quote": {
    "label": "Zitat",
    "is_editable": true,
    "empty": {"text":"Zitat hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("blockquote");
      el.innerHTML = simple_md(box.data.text)
      return el;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Inhalt", name: "text", type: "markdown" }
      ];
      values = {
        text: box.data.text
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      text = data["text"];
      return { "text": text };
    }
  },
  "image": {
    "label": "Bild",
    "is_editable": true,
    "empty": {"source":"https://placekitten.com/100x100", "description": "", "legal": "", "align": "left"},
    "getPreview": function (box) {
      img_container = document.createElement("div");
      img_wrapper = document.createElement("figure");
      img = document.createElement("img");
      img.src = box.data.source;
      img_wrapper.appendChild(img)
      img_container.appendChild(img_wrapper)

      if(box.data.description) {
        img_description = document.createElement("figcaption")
        img_description.innerText = box.data.description;
        img_description.classList.add("f-bold");
        img_wrapper.appendChild(img_description);
      }

      if(box.data.legal) {
        img_legal = document.createElement("figcaption")
        img_legal.innerText = box.data.legal;
        img_wrapper.appendChild(img_legal);
      }

      if(box.data.align == "right" || box.data.align == "push-right") {
        img_wrapper.classList.add("push-right");
        img_reset = document.createElement("div");
        img_reset.classList.add("push-reset");
        img_container.appendChild(img_reset)
      }
      return img_container;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Bild", name: "source", type: "image" },
        { label: "Bildbeschreibung", name: "description", type: "input" },
        { label: "Quelle/Rechtliche Angabe", name: "legal", type: "input" },
        { label: "Ausrichtung", name: "align", type: "select", "options": {
          "left": "linksbündig ohne Umlauf",
          "right": "rechtsbündig ohne Umlauf",
          "push-left": "linksbündig mit Umlauf",
          "push-right": "rechtsbündig mit Umlauf"
        } }
      ];
      values = {
        source: box.data.source,
        description: box.data.description,
        legal: box.data.legal,
        align: box.data.align
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      return {"source": data["source"], "description": data["description"], "legal": data["legal"], "align": data["align"]};
    }
  }
}
