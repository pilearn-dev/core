report_btn = document.getElementById("denial-dialog-deny_btn");
if (report_btn != null) {
    report_btn.addEventListener("click", function () {
        elements = [document.getElementById("denial-dialog-noproof_reason"), document.getElementById("denial-dialog-noadminreq_reason"), document.getElementById("denial-dialog-unnec_reason"), document.getElementById("denial-dialog-other_reason")]
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
        message = document.getElementById("denial-dialog-message").value;
        if (reason == "noproof") {
            message = "Es wurden keine Belege für das beanstandete Verhalten gefunden."
        } else if (reason == "noadminreq") {
            message = "Administratoranrufe sollen nicht für Fehlermeldungen oder andere Probleme genutzt werden, die auch von der Community gelöst werden könnten.\nFehler sollen im globalen Forum mit dem Tag [fehlermeldung] gemeldet werden."
        } else if (reason == "unnec") {
            message = "Meldungen, die Administratoren auffordern Beiträge von Benutzern positiv/negativ zu bewerten oder den Benutzern eine Benutzerstufe oder Reputation zu geben/nehmen sind unnötig und werden abgelehnt."
        }
        document.getElementById('denial-dialog').classList.remove('open');
        denial_callback(message);
    })
}