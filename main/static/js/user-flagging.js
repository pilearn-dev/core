report_btn = document.getElementById(flagging_id + "-report_btn");
if (report_btn != null) {
    report_btn.addEventListener("click", function () {
        reason = document.querySelector("#"+flagging_id+"-content-master [name='reason']:checked").value
        message = document.getElementById(flagging_id + "-message").value;
        $post("user/" +  String(flagging_user) +  "/flag", {
            "type": "flag",
            "reason": reason,
            "message": message
        }, function (resp) {
            master = document.getElementById(flagging_id + "-content-master");
            _ = document.createElement("div");
            if (resp == "{ok}") {
                _.classList.add("success");
                while (master.firstChild) {
                    master.removeChild(master.firstChild);
                }
                _.innerText = "Vielen Dank für die Meldung dieses Benutzers. Wir werden uns darum kümmern.";
                master.appendChild(_);
                __ = document.createElement("button");
                __.innerText = "Ok";
                __.classList.add("less-annoying");
                __.addEventListener("click", function () {
                    document.getElementById(flagging_id).classList.remove('open');
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
