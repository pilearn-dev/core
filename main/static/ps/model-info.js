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
      text = box.data.text.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*?)\`/g, "<code>$1</code>");
      text = text.replace(/\n\n/g, "</p><p>");
      el = document.createElement("div");
      el.innerHTML = "<p>"+text+"</p>"
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
      text = box.data.text.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*?)\`/g, "<code>$1</code>");
      text = text.replace(/\n\n/g, "</p><p>");
      el = document.createElement("div");
      el.innerHTML = "<p>"+text+"</p>"
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
      elel = document.createElement("p");
      elel.innerText = box.data.text;
      el.appendChild(elel);
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
      elel = document.createElement("p");
      elel.innerText = box.data.text;
      el.appendChild(elel);
      return el;
    }
  },
  "quote": {
    "label": "Zitat",
    "is_editable": true,
    "empty": {"text":"Zitat hier einfügen"},
    "getPreview": function (box) {
      text = box.data.text.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*?)\`/g, "<code>$1</code>");
      text = text.replace(/\n\n/g, "</p><p>");
      el = document.createElement("blockquote");
      el.innerHTML = "<p>"+text+"</p>"
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
      text = box.data.text.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*?)\`/g, "<code>$1</code>");
      text = text.replace(/\n\n/g, "</p><p>");
      el = document.createElement("blockquote");
      el.innerHTML = "<p>"+text+"</p>"
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
      m = document.createElement("div");
      ifr = document.createElement("iframe");
      ifr.setAttribute("src", "/upload/dialog");

      el = document.createElement("input");
      el.setAttribute("placeholder", "Image-URL");
      el.value = box.data.source;

      m.appendChild(ifr);
      m.appendChild(el);
      return m;
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
  "wiki-image": {
    "label": "Bild (rechts)",
    "is_editable": true,
    "empty": {"source":"https://placekitten.com/100x100"},
    "getPreview": function (box) {
      el = document.createElement("img");
      el.src = box.data.source;
      return el;
    },
    "getEditor": function (box) {
      m = document.createElement("div");
      ifr = document.createElement("iframe");
      ifr.setAttribute("src", "/upload/dialog");

      el = document.createElement("input");
      el.setAttribute("placeholder", "Image-URL");
      el.value = box.data.source;

      m.appendChild(ifr);
      m.appendChild(el);
      return m;
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
  }
}
