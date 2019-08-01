function simple_md(text) {
    return PiJS.markdown.parse(text)
}

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
  "info-text": {
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
  "multiple-choice": {
    "label": "Multiple Choice",
    "is_editable": true,
    "empty": {"question":"Frage eingeben", "choices": ["Auswahl 1", "Auswahl 2"], "points":1},
    "getPreview": function (box) {
      wrapper = document.createElement("div");

      point_badge_wrapper = document.createElement("div");
      point_badge_wrapper.classList.add("push-right");
      point_badge = document.createElement("span");
      point_badge.innerText = box.data.points + " Pkt.";
      point_badge.classList.add("_badge", "_badge-s-black");

      point_badge_wrapper.appendChild(point_badge);
      wrapper.appendChild(point_badge_wrapper);

      question_body = document.createElement("div");
      question_body.classList.add("fs-subheading");
      question_body.innerHTML = simple_md(box.data.question);

      wrapper.appendChild(question_body);

      for (var i = 0; i < box.data.choices.length; i++) {
        answer_suggestion = document.createElement("div");
        answer_suggestion.classList.add("p1");

        answer_suggestion_radio = document.createElement("input");
        answer_suggestion_radio.classList.add("form-radio");
        answer_suggestion_radio.setAttribute("type", "radio");
        answer_suggestion_radio.setAttribute("disabled", "disabled");

        answer_suggestion.appendChild(answer_suggestion_radio);

        answer_suggestion_label = document.createElement("label");
        answer_suggestion_label.classList.add("form", "form-inline");
        answer_suggestion.appendChild(answer_suggestion_label);


        if(box.data.choices[i].startsWith("*")) {
          answer_suggestion_radio.setAttribute("checked", "checked");
          answer_suggestion_label.innerText = box.data.choices[i].slice(1);
        } else {
          answer_suggestion_label.innerText = box.data.choices[i];
        }

        wrapper.appendChild(answer_suggestion);
      }
      return wrapper;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Fragestellung", name: "question", type: "markdown" },
        { label: "Punkte (maximal)", name: "points", type: "number" },
        { label: "Antwortmöglichkeiten", name: "choices", type: "custom", customId: "QuizInputList" }
      ];


      original_choices = box.data.choices;
      choices = [];

      for (var i = 0; i < original_choices.length; i++) {
        choice = original_choices[i];
        if(choice.startsWith("*"))
          choices.push([true, choice.slice(1)]);
        else
          choices.push([false, choice]);
      }


      values = {
        question: box.data.question,
        points: box.data.points,
        choices: choices,
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      original_choices = data["choices"];
      choices = []

      for (var i = 0; i < original_choices.length; i++) {
        choice = original_choices[i];
        if(choice[0]) {
          choices.push("*" + choice[1]);
        } else {
          choices.push(choice[1]);
        }
      }

      return { "question": data["question"], "points": data["points"], "choices": choices };
    }
  },
  "multiple-answer": {
    "label": "Multiple Answer",
    "is_editable": true,
    "empty": {"question":"Frage eingeben", "choices": ["Auswahl 1", "Auswahl 2", "Auswahl 3"], "points":1},
    "getPreview": function (box) {
      wrapper = document.createElement("div");

      point_badge_wrapper = document.createElement("div");
      point_badge_wrapper.classList.add("push-right");
      point_badge = document.createElement("span");
      point_badge.innerText = box.data.points + " Pkt.";
      point_badge.classList.add("_badge", "_badge-s-black");

      point_badge_wrapper.appendChild(point_badge);
      wrapper.appendChild(point_badge_wrapper);

      question_body = document.createElement("div");
      question_body.classList.add("fs-subheading");
      question_body.innerHTML = simple_md(box.data.question);

      wrapper.appendChild(question_body);

      for (var i = 0; i < box.data.choices.length; i++) {
        answer_suggestion = document.createElement("div");
        answer_suggestion.classList.add("p1");

        answer_suggestion_checkbox = document.createElement("input");
        answer_suggestion_checkbox.classList.add("form-checkbox");
        answer_suggestion_checkbox.setAttribute("type", "checkbox");
        answer_suggestion_checkbox.setAttribute("disabled", "disabled");

        answer_suggestion.appendChild(answer_suggestion_checkbox);

        answer_suggestion_label = document.createElement("label");
        answer_suggestion_label.classList.add("form", "form-inline");
        answer_suggestion.appendChild(answer_suggestion_label);


        if(box.data.choices[i].startsWith("*")) {
          answer_suggestion_checkbox.setAttribute("checked", "checked");
          answer_suggestion_label.innerText = box.data.choices[i].slice(1);
        } else {
          answer_suggestion_label.innerText = box.data.choices[i];
        }

        wrapper.appendChild(answer_suggestion);
      }
      return wrapper;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Fragestellung", name: "question", type: "markdown" },
        { label: "Punkte (maximal)", name: "points", type: "number" },
        { label: "Antwortmöglichkeiten", name: "choices", type: "custom", customId: "QuizInputList" }
      ];


      original_choices = box.data.choices;
      choices = [];

      for (var i = 0; i < original_choices.length; i++) {
        choice = original_choices[i];
        if(choice.startsWith("*"))
          choices.push([true, choice.slice(1)]);
        else
          choices.push([false, choice]);
      }


      values = {
        question: box.data.question,
        points: box.data.points,
        choices: choices,
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      original_choices = data["choices"];
      choices = []

      for (var i = 0; i < original_choices.length; i++) {
        choice = original_choices[i];
        if(choice[0]) {
          choices.push("*" + choice[1]);
        } else {
          choices.push(choice[1]);
        }
      }

      return { "question": data["question"], "points": data["points"], "choices": choices };
    }
  },
  "text-answer": {
    "label": "Textantwort",
    "is_editable": true,
    "empty": {"question":"Frage eingeben", "correct":[], "points":1},
    "getPreview": function (box) {
      wrapper = document.createElement("div");

      point_badge_wrapper = document.createElement("div");
      point_badge_wrapper.classList.add("push-right");
      point_badge = document.createElement("span");
      point_badge.innerText = box.data.points + " Pkt.";
      point_badge.classList.add("_badge", "_badge-s-black");

      point_badge_wrapper.appendChild(point_badge);
      wrapper.appendChild(point_badge_wrapper);

      question_body = document.createElement("div");
      question_body.classList.add("fs-subheading");
      question_body.innerHTML = simple_md(box.data.question);

      wrapper.appendChild(question_body);

      answer_suggestion = document.createElement("div");
      answer_suggestion.classList.add("p1");

      answer_suggestion_input = document.createElement("input");
      answer_suggestion_input.classList.add("form");
      answer_suggestion_input.setAttribute("type", "input");
      answer_suggestion_input.setAttribute("disabled", "disabled");
      answer_suggestion_input.value = box.data.correct.join(", ");

      answer_suggestion.appendChild(answer_suggestion_input);

      wrapper.appendChild(answer_suggestion);
      return wrapper;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Fragestellung", name: "question", type: "markdown" },
        { label: "Punkte (maximal)", name: "points", type: "number" },
        { label: "Korrekte Lösungen", name: "corrects", type: "custom", customId: "QuizInputList", hide_correctness_switch: true, minimum_options: 1 }
      ];


      original_corrects = box.data.correct;
      corrects = [];

      for (var i = 0; i < original_corrects.length; i++) {
        correct = original_corrects[i];
        if(correct.startsWith("*"))
          corrects.push([true, correct.slice(1)]);
        else
          corrects.push([false, correct]);
      }


      values = {
        question: box.data.question,
        points: box.data.points,
        corrects: corrects,
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      original_corrects = data["corrects"];
      corrects = []

      for (var i = 0; i < original_corrects.length; i++) {
        correct = original_corrects[i];
        corrects.push(correct[1]);
      }

      return { "question": data["question"], "points": data["points"], "correct": corrects };
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
    "empty": {"source":"https://placekitten.com/100x100", "description": "", "legal": ""},
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
      return img_container;
    },
    "getEditor": function (box) {
      fields = [
        { label: "Bild", name: "source", type: "image" },
        { label: "Bildbeschreibung", name: "description", type: "input" },
        { label: "Quelle/Rechtliche Angabe", name: "legal", type: "input" }
      ];
      values = {
        source: box.data.source,
        description: box.data.description,
        legal: box.data.legal
      }
      return [fields, values];
    },
    "getEditedContent": function (data) {
      return {"source": data["source"], "description": data["description"], "legal": data["legal"]};
    }
  }
}


QuizInputListEditor = {
  create: function (def, data) {
    MAGIC_MINIMUM_OPTIONS = def.minimum_options || 3;


    wrapper = $("<div>");

    if(!def.hide_correctness_switch) {
      wrapper.append($("<p>").text("Richtige Antwortmöglichkeiten durch Auswahl des Kästchens markieren.").addClass("fs-caption"))
    }

    count = data.length;
    if(count < MAGIC_MINIMUM_OPTIONS) count = MAGIC_MINIMUM_OPTIONS;

    for (var i = 0; i < count; i++) {
      item_wrapper = $("<div>").addClass("horizontal-list respectable-QuizInputList-item");

      correctness_wrapper = $("<div>").addClass("p2");
      is_correct_btn = $("<input type='checkbox'>").addClass("form-checkbox");

      if(!def.hide_correctness_switch) {
        correctness_wrapper.append(is_correct_btn)
        item_wrapper.append(correctness_wrapper);
      }

      label = $("<input>").addClass("form form-inline");
      item_wrapper.append(label);

      if(data[i]) {
        if(data[i][0]) {
          is_correct_btn.attr("checked", "checked");
        }
        label.val(data[i][1]);
      }

      if(i >= MAGIC_MINIMUM_OPTIONS) {
        delete_wrapper = $("<div>").addClass("p1");
        delete_btn = $("<button>").addClass("_btn _btn-danger _btn-sm").text("entfernen");

        delete_btn.on("click", function () {
          $(this).parent().parent().remove();
        })

        delete_wrapper.append(delete_btn)
        item_wrapper.append(delete_wrapper);
      }

      wrapper.append(item_wrapper);
    }

    wrapper.append($("<button>").addClass("_btn _btn-dark _btn-sm").text("Option hinzufügen").on("click", function() {
      item_wrapper = $("<div>").addClass("horizontal-list respectable-QuizInputList-item");

      correctness_wrapper = $("<div>").addClass("p2");
      is_correct_btn = $("<input type='checkbox'>").addClass("form-checkbox");

      if(!def.hide_correctness_switch) {
        correctness_wrapper.append(is_correct_btn)
        item_wrapper.append(correctness_wrapper);
      }

      label = $("<input>").addClass("form form-inline");
      item_wrapper.append(label);

      delete_wrapper = $("<div>").addClass("p1");
      delete_btn = $("<button>").addClass("_btn _btn-danger _btn-sm").text("entfernen");

      delete_btn.on("click", function () {
        $(this).parent().parent().remove();
      })

      delete_wrapper.append(delete_btn)
      item_wrapper.append(delete_wrapper);

      item_wrapper.insertBefore($(this));
    }));

    return wrapper;
  },
  parse: function (def, element) {
    data = [];
    items = element.find(".respectable-QuizInputList-item");

    items.each(function(n, el) {
      el = $(el);
      text = el.find("input[type!='checkbox']").val();
      if(!text.trim().length) { return; }
      if(!def.hide_correctness_switch) {
        data.push([
          el.find("input[type='checkbox']").prop("checked"),
          text
        ])
      } else {
        data.push([
          null,
          text
        ])
      }

    })

    return data;
  }
}
