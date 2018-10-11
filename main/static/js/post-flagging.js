flag_btn = document.getElementById("article_flag_dialog-flag_btn");
if (flag_btn != null) {
    flag_btn.addEventListener("click", function () {
        elements = [document.getElementById("article_flag_dialog-spam_reason"), document.getElementById("article_flag_dialog-offensive_reason"), document.getElementById("article_flag_dialog-duplicate_reason"), document.getElementById("article_flag_dialog-close_reason"), document.getElementById("article_flag_dialog-other_reason")]
        reason = "";
        for (var i = 0; i < elements.length; i++) {
            if (elements[i] == null) {
                continue;
            }
            if (elements[i].checked) {
                reason = elements[i].value;
                break;
            }
        }
        if(reason == "") {
          return;
        }
        subreason = null;
        if(reason == "duplicate") {
          subreason = document.getElementById("article_flag_dialog-dupe_target").value;
          x = subreason.match(/^https?:\/\/[a-z0-9A-Z.]+?\/forum\/([0-9]+?)\/[a-z0-9-]+?\/article\/([0-9]+?)\/[a-z0-9-]+?$/);
          if(!x) {
            alert("Ungültiger Duplikat-Link");
            return
          }
          subreason = {"forum":x[1], "post":x[2]};
        } else if(reason == "close") {
          subreason = document.getElementById("close_reason-list").value;
        }
        message = document.getElementById("article_flag_dialog-message").value;
        $post("forum/"+this.getAttribute("data-post-id")+"/flag", {
            "type": "flag",
            "reason": reason,
            "subreason": subreason,
            "message": message
        }, function (resp) {
            master = document.getElementById("article_flag_dialog-content-master");
            _ = document.createElement("div");
            if (resp == "{ok}") {
                _.classList.add("success");
                while (master.firstChild) {
                    master.removeChild(master.firstChild);
                }
                _.innerText = "Der Nutzer wurde vom System markiert. Sobald genug Nutzer die Sperrung dieses Benutzers verlangen, wird er gesperrt. Vielen Dank für Ihre Hilfe zum Schützen von π-Learn";
                master.appendChild(_);
                __ = document.createElement("button");
                __.innerText = "Ok";
                __.classList.add("less-annoying");
                __.addEventListener("click", function () {
                    document.getElementById("article_flag_dialog").classList.remove('open');
                })
                master.appendChild(__);
            } else {
                if (master.lastChild.classList && master.lastChild.classList.contains("error")) {
                    master.removeChild(master.lastChild);
                }
                _.classList.add("error");
                _.innerText = "Uups. Irgendetwas ist schiefgelaufen. Versuch es bitte erneut. Der Server meldet:";
                __ = document.createElement("pre");
                __.innerText = resp;
                _.appendChild(__);
                master.appendChild(_);
            }
        })
    })
}


close_btn = document.getElementById("article_close_dialog-close_btn");
if (close_btn != null) {
    close_btn.addEventListener("click", function () {
        elements = [document.getElementById("article_close_dialog-duplicate_reason"), document.getElementById("article_close_dialog-off-topic_reason"), document.getElementById("article_close_dialog-unclear_reason"), document.getElementById("article_close_dialog-too-broad_reason"), document.getElementById("article_close_dialog-too-specific_reason"), document.getElementById("article_close_dialog-other_reason")]
        reason = "";
        for (var i = 0; i < elements.length; i++) {
            if (elements[i] == null) {
                continue;
            }
            if (elements[i].checked) {
                reason = elements[i].value;
                break;
            }
        }
        if(reason == "") {
          issueSystemError("Es wurde kein gültiger Grund ausgewählt.");
          return;
        }
        subreason = null;
        if(reason == "duplicate") {
          subreason = document.getElementById("article_close_dialog-dupe_target").value;
          x = subreason.match(/^https?:\/\/[a-z0-9A-Z.]+?\/forum\/([0-9]+?)\/[a-z0-9-]+?\/article\/([0-9]+?)\/[a-z0-9-]+?$/);
          if(!x) {
            issueSystemError("Dieser Duplikat-Link ist ungültig.");
            return
          }
          subreason = x[2] + "";
        } else if(reason == "off-topic") {
          subreason = document.querySelector("#off-topic-reason-list :checked");
          if(subreason == null) {
            issueSystemError("Es wurde kein gültiger Grund ausgewählt.");
            return;
          } else {
            subreason = subreason.value;
          }
        }
        alert(reason);
        $post("forum/"+this.getAttribute("data-post-id")+"/flag", {
            "type": "close",
            "reason": reason,
            "subreason": subreason
        }, function (resp) {
            master = document.getElementById("article_close_dialog-content-master");
            _ = document.createElement("div");
            if (resp == "{ok}") {
              document.getElementById("article_close_dialog").classList.remove('open');
              issueSystemInfo("Vielen Dank, wir werden uns darum kümmern.");
            } else {
                if (master.lastChild.classList && master.lastChild.classList.contains("error")) {
                    master.removeChild(master.lastChild);
                }
                _.classList.add("error");
                _.innerText = "Uups. Irgendetwas ist schiefgelaufen. Versuch es bitte erneut. Der Server meldet:";
                __ = document.createElement("pre");
                __.innerText = resp;
                _.appendChild(__);
                master.appendChild(_);
            }
        })
    })
}
