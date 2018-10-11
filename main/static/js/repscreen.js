function toggle_repscreen() {
    el = document.getElementById("repscreen-area");
    if (el.classList.contains("shown")) {
        el.classList.remove("shown");
        this.classList.remove("open");
    } else {
        this.classList.add("open");
        el.classList.add("shown");
        oth = document.querySelector("#notification-area.shown");
        if(oth) {
          oth.classList.remove("shown");
          document.querySelector("#notification-trigger.open").classList.remove("open");
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
        while (el.firstChild) {
            el.removeChild(el.firstChild);
        }
        _ = document.createElement("h3");
        _.innerHTML = "Reputation";
        el.appendChild(_);
        $post("user/reputation-audit", {}, function (e) {
          data = JSON.parse(e);
          while (el.firstChild) {
              el.removeChild(el.firstChild);
          }
          _ = document.createElement("h3");
          _.innerHTML = "<a href='/u/"+data.userid+"/rep'>Reputation</a>";
          el.appendChild(_);
          tr = document.getElementById("repscreen-trigger");
          if(tr.classList.contains("has-subitem")) {
            tr.innerHTML = "<i class='fa fa-trophy'></i>";
            tr.classList.remove("has-subitem");
          }
          _ = document.createElement("p");
          _.innerHTML = "Deine Reputation beträgt <strong>"+data.reputation+"</strong> Punkte.";
          el.appendChild(_)
          if (data.delta.length > 0) {
            _ = document.createElement("h4");
            _.innerHTML = "Neue Änderungen";
            el.appendChild(_)
          }
          _tab = document.createElement("table");
          _tab.classList.add("rep-table");
          el.appendChild(_tab);
          for (var i = 0; i < data.delta.length; i++) {
            _ = document.createElement("tr");
            d = data.delta[i];
            k = "<th class='" + (d.amount > 0 ? "pos-change" : "neg-change") + "'>" + (d.amount > 0 ? "+" : "") + d.amount_text + "</th><td>" + d.message_html + "</td>";
            _.innerHTML = k;
            _tab.appendChild(_);
          }
          _ = document.createElement("h4");
          _.innerHTML = "Letzte Änderungen";
          el.appendChild(_)
          _tab = document.createElement("table");
          _tab.classList.add("rep-table");
          el.appendChild(_tab);
          for (var i = 0; i < data.latest.length; i++) {
            _ = document.createElement("tr");
            d = data.latest[i];
            k = "<th class='" + (d.amount > 0 ? "pos-change" : "neg-change") + "'>" + (d.amount > 0 ? "+" : "") + d.amount_text + "</th><td>" + d.message_html + "</td>";
            _.innerHTML = k;
            _tab.appendChild(_);
          }
        })
    }
}
el = document.getElementById("repscreen-trigger")
el.addEventListener("click", toggle_repscreen);
