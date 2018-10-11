function edit(field, btn) {
    element = document.getElementById(field);
    if(element == null) {
        return;
    }
    if (field == "password") {
        current_value = "";
    } else if(field== "aboutme") {
        current_value = document.getElementById('aboutme_content').innerText;
    } else {
        current_value = element.innerText;
    }
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
    if (field == "aboutme") {
        btn.outerHTML = "";
        input_element = document.createElement("textarea");
        input_element.classList.add("inline")
        input_element.value = current_value;
        element.appendChild(input_element);
        input_element.focus();
        var simplemde = new SimpleMDE({ element: input_element, forceSync:true, parsingConfig: {strikethrough: false}, promptURLs:true, spellChecker:false });
        btn = document.createElement("button");
        btn.innerText = "Speichern"
        element.appendChild(btn);
        btn.addEventListener("click", function(e) {
          $post("user/set/aboutme", {"new_value": input_element.value, "userid": user_id}, function() {window.location.reload();});
        })
    } else {
        input_element = document.createElement("input");
        input_element.classList.add("inline")
        if (field == "password") {
            input_element.setAttribute("placeholder", "Bitte Passwort neu eingeben!")
            input_element.type = "password"
        }
        input_element.value = current_value;
        element.appendChild(input_element);
        input_element.focus();
        input_element.addEventListener("keypress", function(e) {
            if (e.key == "Enter") {
                $post("user/set/" + field, {"new_value": input_element.value, "userid": user_id});
                element.removeChild(input_element);
                if (field == "password") {
                    element.innerText = "*****"
                } else {
                    element.innerText = input_element.value
                }
            } else if (e.keyCode == 27) {
                element.removeChild(input_element);
                if (field == "password") {
                    element.innerText = "*****"
                } else {
                    element.innerText = current_value
                }
            }
        })
    }
}
