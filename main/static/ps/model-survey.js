var MODEL = {
  "heading": {
    "label": "Überschrift",
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
  "info-text": {
    "label": "Text",
    "is_editable": true,
    "empty": {"text":"Text hier einfügen"},
    "getPreview": function (box) {
      text = box.data.text.replace(/\*\*\*(.*)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*)\`/g, "<code>$1</code>");
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
      text = box.data.text.replace(/\*\*\*(.*)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*)\`/g, "<code>$1</code>");
      text = text.replace(/\n\n/g, "</p><p>");
      el = document.createElement("div");
      el.innerHTML = "<p>"+text+"</p>"
      return el;
    }
  },
  "multiple-choice": {
    "label": "Multiple Choice",
    "is_editable": true,
    "empty": {"question":"Frage eingeben", "choices": ["Auswahl 1", "Auswahl 2"]},
    "getPreview": function (box) {
      el = document.createElement("div");
      _ = document.createElement("p");
      _.innerHTML = box.data.question;
      _.style.fontWeight = "bold";
      el.appendChild(_);
      _ = document.createElement("p");
      _.innerHTML = "☒&nbsp;" + box.data.choices.join("&nbsp; &nbsp;☐&nbsp;");
      el.appendChild(_);
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("div");
      _ = document.createElement("p");
      _.innerText = "Fragestellung";
      el.appendChild(_);
      _ = document.createElement("input");
      _.setAttribute("data-ps-subid", "question");
      _.value = box.data.question;
      el.appendChild(_);
      _ = document.createElement("p");
      _.innerText = "Antwortmöglichkeiten (1 pro Zeile)";
      el.appendChild(_);
      _ = document.createElement("textarea");
      _.setAttribute("data-ps-subid", "choices");
      _.value = box.data.choices.join("\n");
      el.appendChild(_);
      return el;
    },
    "getEditedContent": function (el) {
      q = el.querySelector("input[data-ps-subid='question']");
      c = el.querySelector("textarea[data-ps-subid='choices']");
      return {"question": q.value, "choices": c.value.split("\n")};
    },
    "getView": function (box) {
      el = document.createElement("img");
      el.src = box.data.source;
      return el;
    }
  },
  "text-answer": {
    "label": "Textantwort",
    "is_editable": true,
    "empty": {"question":"Frage eingeben"},
    "getPreview": function (box) {
      el = document.createElement("div");
      _ = document.createElement("p");
      _.innerHTML = box.data.question;
      _.style.fontWeight = "bold";
      el.appendChild(_);
      _ = document.createElement("input");
      _.setAttribute("disabled", "disabled");
      _.setAttribute("placeholder", "Bitte Antwort eingeben");
      el.appendChild(_);
      return el;
    },
    "getEditor": function (box) {
      el = document.createElement("div");
      _ = document.createElement("p");
      _.innerText = "Fragestellung";
      el.appendChild(_);
      _ = document.createElement("input");
      _.setAttribute("data-ps-subid", "question");
      _.value = box.data.question;
      el.appendChild(_);
      return el;
    },
    "getEditedContent": function (el) {
      q = el.querySelector("input[data-ps-subid='question']");
      return {"question": q.value};
    },
    "getView": function (box) {
      el = document.createElement("img");
      el.src = box.data.source;
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
      text = box.data.text.replace(/\*\*\*(.*)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*)\`/g, "<code>$1</code>");
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
      text = box.data.text.replace(/\*\*\*(.*)\*\*\*/g, "<strong><em>$1</em></strong>");
      text = text.replace(/\*\*(.*)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/\*(.*)\*/g, "<em>$1</em>");
      text = text.replace(/\`(.*)\`/g, "<code>$1</code>");
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
  }
}
