function _mmd(text) {
  text = text.replace(/\*\*\*(.*)\*\*\*/g, "<strong><em>$1</em></strong>");
  text = text.replace(/\*\*(.*)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*(.*)\*/g, "<em>$1</em>");
  text = text.replace(/\`(.*)\`/g, "<code>$1</code>");
  text = text.replace(/\n\n/g, "</p><p>");
  return "<p>"+text+"</p>";
}

var MODEL = {
  "heading": {
    "label": "Überschrift 1. Ordnung",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h1");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("h1");
      elel = document.createElement("input");
      elel.value = box.data.text;
      el.appendChild(elel);
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("input");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("h1");
      el.innerText = box.data.text
      return el;
    }
  },
  "subheading": {
    "label": "Überschrift 2. Ordnung",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h2");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("h2");
      elel = document.createElement("input");
      elel.value = box.data.text;
      el.appendChild(elel);
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("input");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("h2");
      el.innerText = box.data.text
      return el;
    }
  },
  "subsubheading": {
    "label": "Überschrift 3. Ordnung",
    "is_editable": true,
    "empty": {"text":"Überschrift"},
    "getPreview": function (box) {
      el = document.createElement("h3");
      el.innerText = box.data.text
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("h3");
      elel = document.createElement("input");
      elel.value = box.data.text;
      el.appendChild(elel);
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("input");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("h3");
      el.innerText = box.data.text
      return el;
    }
  },
  "text": {
    "label": "Text",
    "is_editable": true,
    "empty": {"text":"Text hier einfügen"},
    "getPreview": function (box) {
      text = _mmd(box.data.text);
      el = document.createElement("div");
      el.innerHTML = text;
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("textarea");
      el.value = box.data.text;
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("textarea");
      return {"text": elel.value};
    },
    "getView": function (box) {
      text = _mmd(box.data.text);
      el = document.createElement("div");
      el.innerHTML = text;
      return el;
    }
  },
  "separator": {
    "label": "Trennlinie",
    "is_editable": false,
    "empty": {},
    "getPreview": function (box) {
      return document.createElement("div");
    },
    "getEditor": function (box) {
      return document.createElement("div");;
    },
    "getEditedContent": function (el) {
      return {}
    },
    "getView": function (box) {
      return document.createElement("hr");
    }
  },
  "warnbox": {
    "label": "Warnung",
    "is_editable": true,
    "empty": {"text":"Warnung hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("div");
      el.classList.add("warning");
      el.innerHTML = _mmd(box.data.text);
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("textarea");
      el.value = box.data.text;
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("textarea");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("div");
      el.classList.add("warning");
      el.innerHTML = _mmd(box.data.text);
      return el;
    }
  },
  "errorbox": {
    "label": "Warnung (wichtig!)",
    "is_editable": true,
    "empty": {"text":"Warnung hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("div");
      el.classList.add("user-warning");
      el.innerHTML = _mmd(box.data.text);
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("textarea");
      el.value = box.data.text;
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("textarea");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("div");
      el.classList.add("user-warning");
      el.innerHTML = _mmd(box.data.text);
      return el;
    }
  },
  "quote": {
    "label": "Zitat",
    "is_editable": true,
    "empty": {"text":"Zitat hier einfügen"},
    "getPreview": function (box) {
      el = document.createElement("blockquote");
      el.innerHTML = _mmd(box.data.text)
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("textarea");
      el.value = box.data.text;
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("textarea");
      return {"text": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("blockquote");
      el.innerHTML = _mmd(box.data.text)
      return el;
    }
  },
  "image": {
    "label": "Bild",
    "is_editable": true,
    "empty": {"source":"https://placekitten.com/100x100"},
    "getPreview": function (box) {
      el = document.createElement("img");
      el.src = box.data.source;
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("input");
      el.setAttribute("placeholder", "Image-URL");
      el.value = box.data.source;
      return el;
    },
    "getEditedContent": function (el) {
      elel = el.querySelector("input");
      return {"source": elel.value};
    },
    "getView": function (box) {
      el = document.createElement("img");
      el.src = box.data.source;
      return el;
    }
  },
  "condition-wiki": {
    "label": "Bedingungs-Eintrag",
    "is_editable": true,
    "empty": {"condition":"immer", "title":"Eintrag", "explanation":"Eintragsbeschreibung"},
    "getPreview": function (box) {
      el = document.createElement("details");
      el.innerHTML = _mmd(box.data.explanation);
      elel = document.createElement("summary");
      elel.innerHTML = "<strong>"+box.data.condition+"</strong> &ndash; " + box.data.title;
      el.appendChild(elel);
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("div")
      el1 = document.createElement("input");
      el1.setAttribute("placeholder", "Bedingung");
      el1.setAttribute("data-ps-edit-node", "condition");
      el1.value = box.data.condition;
      el.appendChild(el1);
      el2 = document.createElement("input");
      el2.setAttribute("placeholder", "Eintragsname");
      el2.setAttribute("data-ps-edit-node", "title");
      el2.value = box.data.title;
      el.appendChild(el2);
      el3 = document.createElement("textarea");
      el3.setAttribute("placeholder", "Beschreibung");
      el3.setAttribute("data-ps-edit-node", "explanation");
      el3.value = box.data.explanation;
      el.appendChild(el3);
      return el;
    },
    "getEditedContent": function (el) {
      return {"condition": el.querySelector("[data-ps-edit-node='condition']").value, "explanation": el.querySelector("[data-ps-edit-node='explanation']").value, "title": el.querySelector("[data-ps-edit-node='title']").value};
    },
    "getView": function (box) {
      el = document.createElement("details");
      el.innerHTML = _mmd(box.data.explanation);
      elel = document.createElement("summary");
      elel.innerHTML = "<strong>"+box.data.condition+"</strong> &ndash; " + box.data.title;
      el.appendChild(elel);
      return el;
    }
  }
}
