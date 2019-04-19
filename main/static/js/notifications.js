_nr__ = {
  "helpdesk": "Helpdesk",
  "pm": "Moderatoren-Nachricht",
  "ping": "Benutzer-PING",
  "answered": "Neue Antwort",
  "commented": "Neuer Kommentar",
  "proposal_accept": "Kursvorschlag angenommen"
}

function toggle_notifications() {
    el = document.getElementById("notification-area");
    if (el.classList.contains("shown")) {
        el.classList.remove("shown");
        this.classList.remove("open");
    } else {
        this.classList.add("open");
        el.classList.add("shown");
        oth = document.querySelector("#repscreen-area.shown");
        if(oth) {
          oth.classList.remove("shown");
          document.querySelector("#repscreen-trigger.open").classList.remove("open");
        }
        pos = this.getBoundingClientRect();
        console.log(pos);
        x = pos.x;
        y = pos.y + pos.height + 1;
        el.style.top = String(y) + "px";
        if(x + el.getBoundingClientRect().width >= window.innerWidth - 20) {
            el.style.right = "0px";
            el.style.left = "unset";
        } else {
            el.style.right = "unset";
            el.style.left = String(x)+"px";
        }
        $post("user/notification-clear", {}, function (e) {
          tr = document.getElementById("notification-trigger");
          if(tr.classList.contains("has-subitem")) {
            tr.innerHTML = "<i class='fa fa-exclamation-circle'></i>";
            tr.classList.remove("has-subitem");
          }
        });
        while (el.firstChild) {
            el.removeChild(el.firstChild);
        }
        _ = document.createElement("h3");
        _.innerText = "Benachrichtigungen";
        el.appendChild(_);
        if (NOTIFICATIONS.length == 0) {
            _ = document.createElement("p");
            _.innerText = "keine Benachrichtigungen";
            el.appendChild(_);
        }
        if (NOTIFICATIONS.length != 0)
        {
            the_input = document.createElement("input");
            the_input.classList.add("inline");
            the_input.setAttribute("placeholder", "Suche");
            el.appendChild(the_input);
        }
        all_sub_els = [];
        for (var i = 0; i < NOTIFICATIONS.length; i++) {
            not_ = NOTIFICATIONS[i];
            _nel_ = document.createElement("div");
            _nel_.classList.add("notification-element");
            if (not_.visibility != 0) {
              _nel_.classList.add("not-seen")
            }
                _nel_.classList.add("has-bar");
            _n2 = document.createElement("span");
            _n2.classList.add("element-type");
            tp = _nr__[not_.type];
            if(!tp) {
              tp = "ERR("+not_.type+")";
            }
            _n2.innerText = tp;
            _nel_.appendChild(_n2);
            _n3 = document.createElement("a");
            _n3.classList.add("element-text");
            _n3.innerText = not_.message
            _n3.setAttribute("href", not_.link);
            _nel_.appendChild(_n3);
            el.insertBefore(_nel_, el.firstChild.nextSibling.nextSibling);
            all_sub_els.push(_nel_);
        }
        all_sub_els[0].classList.remove("has-bar");
        if (NOTIFICATIONS.length != 0) {
            _ = document.createElement("p");
            _.innerText = "Insgesamt " + String(NOTIFICATIONS.length) + " Benachrichtigungen";
            el.insertBefore(_, el.firstChild.nextSibling.nextSibling);
            all_sub_els.push(_);
            the_input.addEventListener("keyup", function (event) {
                for (var j = 0; j < all_sub_els.length; j++) {
                    el.removeChild(all_sub_els[j]);
                }
                all_sub_els = [];
                state_filter=-1;
                query = this.value.trim();
                if(query.startsWith("+")) {
                  query=query.substring(1);
                  state_filter = 1;
                } else if(query.startsWith("-")) {
                  query=query.substring(1);
                  state_filter = 0;
                }
                var amount = 0;
                for (var i = 0; i < NOTIFICATIONS.length; i++) {
                    not_ = NOTIFICATIONS[i];
                    if (((query == "") || (not_.message.indexOf(query) != -1)) && (state_filter == -1 || not_.visibility == state_filter)) {
                        amount++;
                        _nel_ = document.createElement("div");
                        _nel_.classList.add("notification-element");
                        if (not_.visibility == 1) {
                          _nel_.classList.add("not-seen")
                        }
                        _nel_.classList.add("has-bar");
                        _n2 = document.createElement("span");
                        _n2.classList.add("element-type");
                        tp = _nr__[not_.type];
                        if(!tp) {
                          tp = "ERR("+not_.type+")";
                        }
                        _n2.innerText = tp;
                        _nel_.appendChild(_n2);
                        _n3 = document.createElement("a");
                        _n3.classList.add("element-text");
                        _n3.innerText = not_.message
                        _n3.setAttribute("href", not_.link);
                        _nel_.appendChild(_n3);
                        el.insertBefore(_nel_, el.firstChild.nextSibling.nextSibling);
                        all_sub_els.push(_nel_);
                    }
                }
                if(all_sub_els.length > 0) {
                    all_sub_els[0].classList.remove("has-bar");
                }
                if (query != "" || state_filter != -1) {
                    _ = document.createElement("p");
                    _.innerText = "Gefunden: " + String(amount) + " von " + String(NOTIFICATIONS.length);
                    el.insertBefore(_, el.firstChild.nextSibling.nextSibling);
                    all_sub_els.push(_);
                } else {
                    _ = document.createElement("p");
                    _.innerText = "Insgesamt " + String(NOTIFICATIONS.length) + " Benachrichtigungen";
                    el.insertBefore(_, el.firstChild.nextSibling.nextSibling);
                    all_sub_els.push(_);
                }
            })
        }
    }
}
el = document.getElementById("notification-trigger");
el.addEventListener("click", toggle_notifications);
