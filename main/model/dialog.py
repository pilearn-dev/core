# coding: utf-8
DIALOG_AREAS = {
    "post_own_or_deleted": {
        "flagging": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "Anderes",
                    "option_message": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                    "option_id": "other",
                    "option_followup": "flagging/other"
                }
            ],
            "title":"Diesen Beitrag melden",
            "previous": None
        },
        "flagging/other": {
            "response":"dialog",
            "dialog_style":"textarea",
            "ops": {
                "label": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                "placeholder": "Beschreibe das Problem ausführlich und gebe Beispiele."
            },
            "title":"Melden / Anderes",
            "previous": "flagging"
        }
    },
    "post_closed": {
        "flagging": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "SPAM",
                    "option_message": "Dieser Beitrag enthält Werbung, die den inhaltlichen Wert nicht steigert oder die versteckt ist.",
                    "option_id": "spam",
                    "option_followup": None
                },
                {
                    "option_label": "Beleidigung",
                    "option_message": "Dieser Post enthält beleidigende, verletzende oder diskriminierende Inhalte oder verstößt auf eine andere Art gegen den <a href='/help/legal/coc'>Code of Conduct</a> oder das geltende Recht.",
                    "option_id": "offensive",
                    "option_followup": None
                },
                {
                    "option_label": "Anderes",
                    "option_message": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                    "option_id": "other",
                    "option_followup": "flagging/other"
                }
            ],
            "title":"Diesen Beitrag melden",
            "previous": None
        },
        "flagging/other": {
            "response":"dialog",
            "dialog_style":"textarea",
            "ops": {
                "label": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                "placeholder": "Beschreibe das Problem ausführlich und gebe Beispiele."
            },
            "title":"Melden / Anderes",
            "previous": "flagging"
        }
    },
    "post_no_close_priv": {
        "flagging": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "SPAM",
                    "option_message": "Dieser Beitrag enthält Werbung, die den inhaltlichen Wert nicht steigert oder die versteckt ist.",
                    "option_id": "spam",
                    "option_followup": None
                },
                {
                    "option_label": "Beleidigung",
                    "option_message": "Dieser Post enthält beleidigende, verletzende oder diskriminierende Inhalte oder verstößt auf eine andere Art gegen den <a href='/help/legal/coc'>Code of Conduct</a> oder das geltende Recht.",
                    "option_id": "offensive",
                    "option_followup": None
                },
                {
                    "option_label": "Schließen",
                    "option_message": "Dieser Beitrag passt nicht in dieses Forum, ist unklar, zu allgemein oder wurde bereits früher gefragt und beantwortet..",
                    "option_id": "closure",
                    "option_followup": "flagging/closure"
                },
                {
                    "option_label": "Anderes",
                    "option_message": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                    "option_id": "other",
                    "option_followup": "flagging/other"
                }
            ],
            "title":"Diesen Beitrag melden",
            "previous": None
        },
        "flagging/other": {
            "response":"dialog",
            "dialog_style":"textarea",
            "ops": {
                "label": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                "placeholder": "Beschreibe das Problem ausführlich und gebe Beispiele."
            },
            "title":"Melden / Anderes",
            "previous": "flagging"
        },
        "flagging/closure": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "exaktes Duplikat",
                    "option_message": "Andere Benutzer hatten dieses Problem auch und fanden bereits eine Antwort.",
                    "option_id": "duplicate",
                    "option_followup": "flagging/closure/duplicate"
                },
                {
                    "option_label": "in diesem Forum unpassend",
                    "option_message": "Dieser Beitrag passt in Bezug auf das Beitragsthema nicht in dieses Forum.",
                    "option_id": "off-topic",
                    "option_followup": "flagging/closure/off-topic"
                },
                {
                    "option_label": "unklar",
                    "option_message": "Ich finde die Frage-/Problemstellung unverständlich.",
                    "option_id": "unclear",
                    "option_followup": None
                },
                {
                    "option_label": "zu allgemein",
                    "option_message": "Eine Antwort auf diesen Beitrag wäre zu komplex (könnte ein Buch füllen) oder es gibt keine Möglichkeit eine eindeutig richtige Antwort zu finden.",
                    "option_id": "too-broad",
                    "option_followup": None
                },
                {
                    "option_label": "zu spezifisch",
                    "option_message": "Dieser Beitrag fordert nur eine Lösung (und keinen Lösungsweg) und hilft daher niemandem weiter.",
                    "option_id": "too-specific",
                    "option_followup": None
                }
            ],
            "title":"Melden / Schließen",
            "previous": "flagging"
        }
    },
    "post_close_priv": {
        "flagging": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "SPAM",
                    "option_message": "Dieser Beitrag enthält Werbung, die den inhaltlichen Wert nicht steigert oder die versteckt ist.",
                    "option_id": "spam",
                    "option_followup": None
                },
                {
                    "option_label": "Beleidigung",
                    "option_message": "Dieser Post enthält beleidigende, verletzende oder diskriminierende Inhalte oder verstößt auf eine andere Art gegen den <a href='/help/legal/coc'>Code of Conduct</a> oder das geltende Recht.",
                    "option_id": "offensive",
                    "option_followup": None
                },
                {
                    "option_label": "Anderes",
                    "option_message": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                    "option_id": "other",
                    "option_followup": "flagging/other"
                }
            ],
            "title":"Diesen Beitrag melden",
            "previous": None
        },
        "flagging/other": {
            "response":"dialog",
            "dialog_style":"textarea",
            "ops": {
                "label": "Ein anderes Problem, das die Einwirkung eines Moderators benötigt.",
                "placeholder": "Beschreibe das Problem ausführlich und gebe Beispiele."
            },
            "title":"Melden / Anderes",
            "previous": "flagging"
        },
        "closure": {
            "response":"dialog",
            "dialog_style":"select",
            "ops": [
                {
                    "option_label": "exaktes Duplikat",
                    "option_message": "Andere Benutzer hatten dieses Problem auch und fanden bereits eine Antwort.",
                    "option_id": "duplicate",
                    "option_followup": "closure/duplicate"
                },
                {
                    "option_label": "in diesem Forum unpassend",
                    "option_message": "Dieser Beitrag passt in Bezug auf das Beitragsthema nicht in dieses Forum.",
                    "option_id": "off-topic",
                    "option_followup": "closure/off-topic"
                },
                {
                    "option_label": "unklar",
                    "option_message": "Ich finde die Frage-/Problemstellung unverständlich.",
                    "option_id": "unclear",
                    "option_followup": None
                },
                {
                    "option_label": "zu allgemein",
                    "option_message": "Eine Antwort auf diesen Beitrag wäre zu komplex (könnte ein Buch füllen) oder es gibt keine Möglichkeit eine eindeutig richtige Antwort zu finden.",
                    "option_id": "too-broad",
                    "option_followup": None
                },
                {
                    "option_label": "zu spezifisch",
                    "option_message": "Dieser Beitrag fordert nur eine Lösung (und keinen Lösungsweg) und hilft daher niemandem weiter.",
                    "option_id": "too-specific",
                    "option_followup": None
                }
            ],
            "title":"Diesen Beitrag schließen",
            "previous": None
        },
        "closure/duplicate": {
            "response":"dialog",
            "dialog_style":"choice",
            "ops": {
                "label": "Welcher Beitrag beantwortet diesen?",
                "placeholder": "Beitragstitel oder #ID"
            },
            "title":"Schließen / Duplikat",
            "previous": "closure"
        }
    },
    "post": {
        "mod": {
            "response": "dialog",
            "dialog_style": "select",
            "ops": [
                {
                    "option_label": "Beitrag einfrieren",
                    "option_message": "Dieser Beitrag kann nicht mehr bearbeitet, bewertet oder moderiert werden.",
                    "option_id": "freeze",
                    "option_followup": "mod/freeze"
                },
                {
                    "option_label": "Nachricht setzen",
                    "option_message": "Eine Nachricht auswählen, die unter dem Beitrag angezeigt wird.",
                    "option_id": "message",
                    "option_followup": "mod/message"
                },
                {
                    "option_label": "Wiki",
                    "option_message": "Diesen Beitrag in einen Wiki-Modus schalten, so dass der Beitrag von allen Benutzern bearbeitet werden kann.",
                    "option_id": "wiki",
                    "option_followup": None
                }
            ],
            "title": "Moderatoren-Tools",
            "previous": None
        }
    }
}
