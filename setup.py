import os, sys, json, hashlib
import sqlite3 as lite

print("""
## ###################################
##      Setup Script for pi-Learn     
## ###################################
""".strip())

print()
print("""
#  -----------------------------------
#  1. Set up the pidata.json
#  -----------------------------------
""".strip())

pidata = {
    "mail_service": "none",
    "mail_configuration": {
        "addr_base": "@example.com",
        "user": "",
        "password": "",
        "smtp_srv": "",
        "smtp_port": 587
    },
    "db_host": "sqlite:///" + os.path.join(os.getcwd(), "databases", "pilearn.db")
}

print("Do you want to enable emails to be send to your users?")

if input("(y/N) ").lower() == "y":
    pidata["mail_service"] = "smtp"

    print("""
You will need to configure these settings in order to be able
to send emails:

Base URL        The base URL from which the emails are going to be send.
                If you want your emails to be send from
                    nicht-antworten@example.com,
                you need to enter `example.com`.
Mail User       The user account, from which the emails shall be send.
                Must exist; configured by your hoster/provider.
Mail Password   The password for the mail user.
SMTP Server     Your mail server (SMTP server) domain name.
                Often similar to mail.example.com.
SMTP Port       The port for the SMTP server. Defaults to 587.
                configured by your hoster/provider.
------------------------------------------------------------------
""".strip())

    pidata["mail_configuration"]["addr_base"] = "@" + input("Base URL: ")
    pidata["mail_configuration"]["user"] = input("Mail User: ")
    pidata["mail_configuration"]["password"] = input("Mail Password: ")
    pidata["mail_configuration"]["smtp_srv"] = input("SMTP Server: ")
    port = input("SMTP Port (587): ")
    try:
        port = int(port)
        if port == 0: port = 587
    except:
        port = 587
    pidata["mail_configuration"]["smtp_port"] = port

else:
    print("Do you want to save the emails to disk? (useful for development)")

    if input("(Y/n) ").lower() != "n":
        pidata["mail_service"] = "fileoutput"
        try:
            os.mkdir("mailoutput")
        except:
            print("Warning! Could not create mailoutput folder. Check if it already exists or whether there is a permission error.")

print("""
------------------------------------------------------------------
""".strip())

json_pretty = json.dumps(pidata, sort_keys=True, indent=4)
json = json.dumps(pidata, sort_keys=True)

print("Printing to pidata.json:")
print()
print(json_pretty)
print()
print("""
------------------------------------------------------------------
""".strip())
print()

try:
    f = open("pidata.json", "w")
    f.write(json)
    f.close()
except:
    print("Error occured! Check your file system permissions.")
    sys.exit(1)
finally:
    print("Success! Config written to pidata.json.")

print()
print()
print()

print()
print("""
#  -----------------------------------
#  2. Set up the database
#  -----------------------------------
""".strip())
print()

print("Do you want to initialize the database? (only on first run)")
if input("(Y/n) ").lower() == "n":
    sys.exit(0)


SQL = """
CREATE TABLE courses (id integer PRIMARY KEY AUTOINCREMENT, topicid integer, title varchar, shortdesc varchar, longdesc text, requirements text, byline varchar, sponsorid integer, state integer, picture_url VARCHAR(60), manual_enrollment TINYINT);
CREATE TABLE enrollments (id integer PRIMARY KEY AUTOINCREMENT, courseid integer, userid integer, lastunitid integer, permission tinyint);
CREATE TABLE visits (id integer PRIMARY KEY AUTOINCREMENT, courseid integer, userid integer, unitid integer, data text);
CREATE TABLE topics (id integer PRIMARY KEY AUTOINCREMENT, name varchar, title varchar, excerpt varchar, description text, giveable integer);
CREATE TABLE pull_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, author INT, branch_id INT, course_id INT, title VARCHAR (150), description TEXT (1050), proposal_date INT, decision TINYINT, decision_date INT, hide_as_spam BOOLEAN);
CREATE TABLE units (id integer PRIMARY KEY AUTOINCREMENT, title varchar, courseid integer, content text, type varchar, parent integer, availible integer, unit, unit_order integer);
CREATE TABLE branches (id INTEGER PRIMARY KEY AUTOINCREMENT, author INT, course_id INT, pull_request INT, abandoned BOOLEAN, abandoned_date INT, decision TINYINT, decision_date INT, hide_as_spam BOOLEAN, delta_factor SMALLINT);
CREATE TABLE proposals (id integer PRIMARY KEY AUTOINCREMENT, topicid integer, title varchar, shortdesc varchar, longdesc text, requirements text, proposer integer, score integer, declined integer, decline_reason text, deleted integer, delete_reason text, courseid integer, proposal_time INT);
CREATE TABLE branch_overrides (id INTEGER PRIMARY KEY, branch INT, overrides INT, parent_unit INT, parent_override INT, title VARCHAR (150), content TEXT, type VARCHAR (25), unit_order INT, changed BOOLEAN, created BOOLEAN);
CREATE TABLE commitments (id INTEGER PRIMARY KEY, proposal_id INT, course_id INT, user_id INT, worth FLOAT, fulfilled TINYINT, creation_time INT, activation_time INT, invalidated TINYINT);
CREATE TABLE nominations (id INTEGER PRIMARY KEY, election_id INT, message TEXT, answer_score FLOAT, candidate INT, state TINYINT);
CREATE TABLE election_votes (id INTEGER PRIMARY KEY, election_id INT, voter INT, ballot TEXT);
CREATE TABLE elections (id INTEGER PRIMARY KEY, title VARCHAR (250), message TEXT, places TINYINT, position VARCHAR (50), state TINYINT, minvoterep INT, mincandrep INT);
CREATE TABLE election_questions (id INTEGER PRIMARY KEY, election_id INT, nomination_id INT, is_community TINYINT, content TEXT, answer TEXT, state TINYINT, asked_date INT, author INT);
CREATE TABLE reopen_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT);
CREATE TABLE announcements (id INTEGER PRIMARY KEY, forum INT, link VARCHAR (150), title VARCHAR (150), start_date INT, end_date INT, show_from INT, show_until INT, is_featured_banner TINYINT);
CREATE TABLE closure_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR (4), reason VARCHAR (20), comment TEXT);
CREATE TABLE forum_tags (id INTEGER PRIMARY KEY AUTOINCREMENT, forum_id INTEGER, name VARCHAR (30), excerpt TEXT (300), deprecation_notice TEXT (150), redirects_to INTEGER, applicable BOOLEAN, mod_only BOOLEAN);
CREATE TABLE article_revisions (id INTEGER PRIMARY KEY, forumID INT, articleID INT, new_title VARCHAR (250), editor INT, new_content TEXT, new_tags TEXT, review_id INT, comment VARCHAR (250), type VARCHAR (20), timestamp INT);
CREATE TABLE post_undeletion_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR (4), reason VARCHAR (20), comment TEXT);
CREATE TABLE closure_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT);
CREATE TABLE forum_comments (id INTEGER PRIMARY KEY, post_type VARCHAR (10), post_id INT, post_forum INT, comment_score INT, comment_author INT, deleted TINYINT, deletedby TINYINT, annoyingness TINYINT, creation_time INT, content TEXT);
CREATE TABLE post_deletion_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR (4), reason VARCHAR (20), comment TEXT);
CREATE TABLE post_undeletion_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT);
CREATE TABLE reopen_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT);
CREATE TABLE forum_tag_associations (post_id INTEGER, tag_id INTEGER);
CREATE TABLE post_undeletion_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT);
CREATE TABLE undeletion_votes (postType VARCHAR (20), postId INT, voteOwner INT, voteCastDate INT, active TINYINT);
CREATE TABLE comment_action (id INTEGER PRIMARY KEY, comment_id INT, user_id INT, validated TINYINT, comment VARCHAR (50), "action" VARCHAR (20));
CREATE TABLE post_notices (id INTEGER PRIMARY KEY, name VARCHAR (50), body TEXT (500), active TINYINT, use_for_lock TINYINT, use_for_general TINYINT);
CREATE TABLE post_deletion_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT);
CREATE TABLE deletion_votes (postType VARCHAR (20), postId INT, voteOwner INT, voteCastDate INT, active TINYINT);
CREATE TABLE articles (id INTEGER PRIMARY KEY, forumID INT, title VARCHAR (150), author INT, score INT, content TEXT, tags TEXT, awardRep SMALLINT, awardBy INT, awardMessage TEXT, awardStarted INT, awardEnded INT, hasAcceptedAnswer TINYINT, pinned TINYINT, frozen TINYINT, frozenBy INT, frozenMessage TEXT, frozenAsLock TINYINT, closed TINYINT, closureReason VARCHAR (15), deleted TINYINT, deletionReason VARCHAR (15), protected TINYINT, protectionBy INT, moderatorNotice TEXT, creation_date INT, last_edit_date INT, last_editor INT, last_activity_date INT);
CREATE TABLE answers (id INTEGER PRIMARY KEY, forumID INT, articleID, author INT, score INT, content TEXT, awardRep SMALLINT, awardBy INT, awardMessage TEXT, isAcceptedAnswer TINYINT, frozen TINYINT, frozenBy INT, frozenMessage, deleted TINYINT, moderatorNotice TEXT, deletionReason VARCHAR (15), creation_date INT, last_edit_date INT, last_editor INT);
CREATE TABLE score_votes (id INTEGER PRIMARY KEY, user_id INT, direction TINYINT, reputation TINYINT, target_type VARCHAR (20), target_id INT, nullified TINYINT);
CREATE TABLE post_deletion_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT);
CREATE TABLE closure_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT);
CREATE TABLE reopen_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR (4), reason VARCHAR (20), comment TEXT);
CREATE TABLE answer_revisions (id INTEGER PRIMARY KEY, forumID INT, articleID INT, answerID INT, editor INT, new_content TEXT, review_id INT, comment VARCHAR (250), type VARCHAR (20), timestamp INT);
CREATE TABLE closure_reasons (id INTEGER PRIMARY KEY, name VARCHAR (40), ui_name VARCHAR (40), description TEXT (300), requires_post TINYINT, requires_subreason TINYINT, active TINYINT, not_in_global_forum TINYINT, not_in_course_forum TINYINT, parent INT);
CREATE TABLE help_category (id INTEGER PRIMARY KEY, active TINYINT, cat_symbol VARCHAR (30), url_part VARCHAR (30), title VARCHAR (100), original_excerpt VARCHAR (300), override_excerpt VARCHAR (300), editable_by_admin TINYINT, newpage_by_admin TINYINT);
CREATE TABLE help_entry (id INTEGER PRIMARY KEY, master_page INT, active TINYINT, template VARCHAR (25), help_cat INT, url_part VARCHAR (30), url VARCHAR (100), title VARCHAR (300), original_content TEXT, override_content TEXT, editable_by_admin TINYINT, subpage_by_admin TINYINT, is_deprecated TINYINT, is_pinned TINYINT, last_change INT, last_editor INT);
CREATE TABLE surveys (id INTEGER PRIMARY KEY, title VARCHAR (100), content TEXT, results TEXT, state TINYINT, associated_forum INT, survey_owner INT);
CREATE TABLE survey_responses (id INTEGER PRIMARY KEY, survey_id INT, responder_id INT, content TEXT);
CREATE TABLE reputation (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR (20), message TEXT, amount INT, recognized TINYINT, given_date int);
CREATE TABLE password_reset_requests (id INTEGER PRIMARY KEY, user_id INT, login_method_id INT, creation_date INT, deletion_date INT, verification_code VARCHAR (7));
CREATE TABLE modmsg_messages (id INTEGER PRIMARY KEY, thread_id INT, submitted_by INT, submission_time INT, message_receiver INT, content TEXT, suspension_length INT, template INT, closed_thread TINYINT);
CREATE TABLE modmsg_threads (id INTEGER PRIMARY KEY, initiated_by INT, last_activity INT, contacted_user INT, closed TINYINT);
CREATE TABLE modmsg_templates (id INTEGER PRIMARY KEY, title VARCHAR (50), content TEXT, may_be_used TINYINT);
CREATE TABLE badge_associations (userid INT, badgeid INT, data TEXT, recognized TINYINT, given_date INT);
CREATE TABLE user_roles (id INTEGER PRIMARY KEY, name VARCHAR (50), is_mod TINYINT, is_dev TINYINT, is_team TINYINT);
CREATE TABLE notifications (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR (10), message TEXT, link VARCHAR (100), visible TINYINT);
CREATE TABLE login_methods (id INTEGER PRIMARY KEY, user_id INT, provider VARCHAR (20), email VARCHAR (100), password VARCHAR (100), last_used INT, last_verified INT);
CREATE TABLE badges (id INTEGER PRIMARY KEY, name VARCHAR (40), class VARCHAR (10), description TEXT, internal_id VARCHAR (50));
CREATE TABLE user_uploads (id INTEGER PRIMARY KEY, user_id INT, file_path VARCHAR (50), removed_by INT, upload_at INT, file_size INT);
CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR (50), realname VARCHAR (100), email VARCHAR (100), login_provider VARCHAR (20), password VARCHAR (100), aboutme TEXT, deleted TINYINT, banned TINYINT, ban_reason VARCHAR (30), ban_end INT, frozen TINYINT, role INT, reputation INT, suspension TEXT, labels TEXT, profile_image VARCHAR (100), last_login INT, last_email_change INT, last_password_reset INT, mergeto INT, profile_place VARCHAR (100), profile_website VARCHAR (150), profile_twitter VARCHAR (150), profile_projects TEXT, member_since INT, certificate_full_name VARCHAR (150));
CREATE TABLE custom_flag (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR (30), queue_id INT, state TINYINT, flagger_id INT, comment TEXT, response TEXT);
CREATE TABLE annotations (id INTEGER PRIMARY KEY, user_id INT, creator_id INT, creation_date INT, is_hidden TINYINT, content TEXT, type VARCHAR (20));
CREATE TABLE user_preference_overrides (user_id INT, pref_key VARCHAR (50), value TEXT);
CREATE TABLE custom_flaglist (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR (30), state TINYINT, handler INT);
CREATE TABLE reviewbans (id INTEGER PRIMARY KEY, queue VARCHAR (25), user_id INT, given_by INT, cancelled_by INT, start_date INT, end_date INT, invalidated TINYINT, comment TEXT);
CREATE TABLE settings ( setting_group VARCHAR(30), setting_key VARCHAR(30) PRIMARY KEY, setting_value TEXT, setting_description VARCHAR(250) );
""".strip()

print("Initializing database...")
print()

try:
    os.mkdir("databases")
except:
    print("Warning! Could not create databases folder. Check if it already exists or whether there is a permission error.")

con = lite.connect('databases/pilearn.db')
cur = con.cursor()

try:
    cur.executescript(SQL)
except Exception as err:
    print("Error occured! SQL Error:", err)
    sys.exit(1)
else:
    print("Success! Database initialized.")
finally:
    if con:
        con.close()



print()
print("""
#  -----------------------------------
#  3. Seed the database
#  -----------------------------------
""".strip())
print()

print()
print("Seeding settings...")
print()

seeds_settings = [
    ["Identität", "site-name", "Open Learn", "Der Name der Seite in reiner Textform"],
    ["Identität", "site-short-name", "Open Learn", "Der Name der Seite in reiner Textform (Kurzform)"],
    ["Identität", "site-label", "Open Learn", "Der Name der Seite, wie er in der Navigationsleiste ausgegeben wird (<x> enthält Attribute, wie z.B. beta)"],
    ["Logging", "logging-errors-sentry-key", "", "Der geheime Schlüssel für das Sentry.io Fehleranalyse-Tool"],
    ["Logging", "logging-matomo-id", "", "Die Nummer der Seite im Matomo-Analytics-Tool"],
    ["Logging", "logging-matomo-url", "", "Die Matomo-Analytics-Tool-URL"],
    ["Zugang", "access-private", "0", "Ob diese Seite zugriffsbeschränkt ist"],
    ["Zugang", "access-private-token", "", "Das Geheimnis, das als Masterpasswort für die Zugriffsbeschränkung verwendet wird"],
    ["Zugang", "access-private-notice", "", "Die Nachricht, die für Unbefugte angezeigt wird"],
    ["Zugang", "access-allow-password", "1", "Ob die Zugriffsbeschränkung mit einem Passwort umgangen werden kann"],
    ["Zugang", "access-allow-password-value", "", "Das Passwort, mit dem die Beschränkung umgangen werden könnte"],
    ["Features", "limit-course-creation", "no", "Hiermit haben nur Nutzer mit der Team-Rolle die Berechtigung, Kurse zu erstellen."],
    ["Features", "enable-mathjax", "1", "Ob MathJax (mathematische Notation) geladen werden soll"],
    ["Features", "enable-mathjax-tokens-block", "[math] [/math]", "Die MathJax-Begrenzungen (Blöcke)"],
    ["Features", "enable-mathjax-tokens-inline", "[m] [/m]", "Die MathJax-Begrenzungen (Inline)"],
    ["Identität", "site-language", "de", "Die Sprache der Seite (de/en)"],
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO settings (setting_group, setting_key, setting_value, setting_description) VALUES (?, ?, ?, ?)"
for setting in seeds_settings:
    cur.execute(sql, setting)

con.commit()
con.close()

print()
print("Seeding settings successful.")
print("You'll probably want to change the default.")
print()


print()
print("Seeding topics...")
print()

seeds_topics = [
    ["kurse", "Kurse", "", "", True]
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO topics (name, title, excerpt, description, giveable) VALUES (?, ?, ?, ?, ?)"
for topic in seeds_topics:
    cur.execute(sql, topic)

con.commit()
con.close()

print()
print("Seeding topics successful.")
print("You'll probably want to change the default.")
print()





print()
print("Seeding post_notices...")
print()

seeds_post_notices = [
    [1, "Konflikte über Inhalt", "<p>Dieser Beitrag wurde eingefroren, bis alle Streitigkeiten über den Inhalt beendet sind. Nutze das <a href='/f/0'>globale Forum</a> für alle Diskussionen.</p>", True, True, False],
    [2, "Zu viele Kommentare", "<p>Dieser Beitrag wurde eingefroren, da er eine hohe Anzahl an Kommentaren angezogen hat, die entfernt werden mussten. Nutze das <a href='/f/0'>globale Forum</a> für Diskussionen über den Inhalt eines Beitrags.</p>", True, True, False],
    [3, "Historische Relevanz", "<p>Dieser Beitrag hat historische Bedeutung aufgrund seines Alters und seiner Verbreitung, stellt aber <strong>kein gutes Beispiel für einen Beitrag in diesem Forum</strong> mehr dar und sollte keinenfalls als Anlass genommen werden, einen ähnlichen Beitrag zu posten.</p><p>Dieser Beitrag und seine Antworten wurden in der Zeit stehen gelassen und können nicht beeinflusst werden.</p>", True, True, False],
    [11, "Keine Antwort", "<p>Wir erwarten, dass Antworten bestmöglich versuchen, das konkrete Problem des Fragestellers zu lösen.</p><p><strong>Antworten, bei denen <em>kein Lösungsansatz erkennbar</em> ist, werden gelöscht.</strong></p>", True, False, True],
    [12, "Belege erforderlich", "<p>Bitte belege deine Antwort <strong>mit Zitaten, Quellen und anderen, anerkannten und nachvollziehbaren Materialien</strong>.</p><p>Antworten, die nicht hinreichend belegt werden, sind nicht hilfreich für andere Benutzer und können entfernt werden.</p>", True, False, True],
    [13, "Aktuelles Ereignis", "<p><strong>Dieser Beitrag betrifft ein aktuelles Ereignis, zu dem sich die Kenntnislage <em>schnell und häufig ändern</em> kann.</strong></p><p>Daher ist es von besonderer Bedeutung, sowohl Verweise zu <em>offizielle Quellen</em> anzugeben, als auch <em>die aktuelle Fassung</em> mit hinreichend genauen Zeitangaben zu zitieren.</p>", True, False, True]
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO post_notices (id, name, body, active, use_for_lock, use_for_general) VALUES (?, ?, ?, ?, ?, ?)"
for post_notice in seeds_post_notices:
    cur.execute(sql, post_notice)

con.commit()
con.close()

print()
print("Seeding post_notices successful.")
print()



print()
print("Seeding closure_reasons...")
print()

seeds_closure_reasons = [
    [1, "Duplikat", "bereits gefragt und beantwortet", "Andere hatten dieses Problem auch und fanden bereits eine Antwort", True, False, True, False, False, None],
    [2, "Off Topic", "off-topic", "Dieser Beitrag passt nicht in das ${forum_name}, da ...", False, True, True, False, False, None],
    [3, "Unklar", "unklar", "Es ist nicht klar, was in diesem Beitrag gefragt wird, wie eine Antwort auszusehen hat oder es fehlen kritische Details, die diese Frage nicht beantwortbar machen.", False, False, True, False, False, None],
    [4, "Zu Allgemein", "zu allgemein", "Dieser Beitrag besteht aus mehreren Fragen, hat zu viele mögliche, ununterscheidbar korrekte Antworten oder fordert übertrieben lange Antworten.", False, False, True, False, False, None],
    [5, "Nicht Konstruktiv", "nicht konstruktiv", "Diese Frage kann nur in einer Weise beantwortet werden, die für niemanden wirklich vorteilhaft ist. Es ist nicht möglich, durch eine Antwort auf diese Frage etwas neues zu lernen, außer die Lösung für das spezifische Problem des Fragestellenden", False, False, True, False, False, None],
    [101, "", "off-topic", "Fragen zu Inhalten aus Kursen, Meldungen zu Fehlern in Kursen und Verbesserungsideen zu Kursen gehören nicht in das globale Forum, sondern in das jeweilige Kursforum.", False, False, True, True, False, "2"],
    [102, "", "off-topic", "Support-Fragen, Fehlermeldungen oder Verbesserungsideen zur π-Learn-Software sowie Diskussionen zu Community-Richtlinien gehören nicht in ein Kursforum, sondern in das globale Forum.", False, False, True, False, True, "2"],
    [103, "", "off-topic", "Diese Frage passt nicht in das ${forum_name}, in dem Rahmen, der im Hilfezentrum beschrieben wird.", False, False, False, False, True, "2"]
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO closure_reasons (id, name, ui_name, description, requires_post, requires_subreason, active, not_in_global_forum, not_in_course_forum, parent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
for closure_reason in seeds_closure_reasons:
    cur.execute(sql, closure_reason)

con.commit()
con.close()

print()
print("Seeding closure_reasons successful.")
print()




print()
print("Seeding help_category...")
print()

seeds_help_category = [
    [True, "fa-book", "legal", "Verbindliches", "Nutzungsbedingungen, Code of Conduct und weitere verbindliche Dokumente", "", False, False],
    [True, "fa-quote-left", "concept", "Konzept", "Was π-Learn ist, sein soll und wie es funktioniert", "", False, False],
    [True, "fa-trophy", "gamification", "Gamification", "Das Reputationssystem und Privilegien", "", False, False],
    [True, "fa-user-circle", "faq", "FAQ", "Häufig gestellte Fragen", "", False, False]
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO help_category (active, cat_symbol, url_part, title, original_excerpt, override_excerpt, editable_by_admin, newpage_by_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
for help_category in seeds_help_category:
    cur.execute(sql, help_category)

con.commit()
con.close()

print()
print("Seeding help_category successful.")
print()




print()
print("Seeding help_entry...")
print()

seeds_help_entry = [
    [0, True, "default", 1, "terms", "legal/terms", "Nutzungsbedingungen", "<p><a href=\"/legal/terms\">Siehe hier!</a></p>", "", False, False, False, True, 0, 0],
    [0, False, "default", 2, "teampage", "concept/teampage", "Team: Benutzerkennungen", """Syntax: section: [-1, "<name>", "<description>"] member: [<user_id or 0>, "<name>", ["<role1>", "<role2>"], "<comment>", {"image":"<img>","website":"<url>","twitter":"<handle>"] <!-- end comment --> []""", "", False, False, False, False, 0, 0],
    [0, True, "default", 1, "coc", "legal/coc", "Code of Conduct", """*Auf dieser Webseite versuchen wir eine freundliche, offene und reichhaltige Lernumgebung zu schaffen. Daher haben wir uns diesen Code of Conduct gegeben:*

### Sei konstruktiv!

Versuche die Seite zu verbessern.

- *Kurse anbieten*, *Fragen stellen*, *Antworten schreiben* und *Beiträge verbessern* &mdash; all das sind Aktionen, die die Seite voranbringen.
- Gib *konstruktive Kritik*, d.h. zeige nicht nur Fehler sondern auch mögliche Alternativen auf.
- Sei *auf das Wesentliche konzentriert*. Vereinzelte Späße sind in Ordnung, solange sie andere Benutzer nicht vom ernsthaften Benutzen der Webseite ablenken. 

### Sei höflich!

Gehe höflich mit anderen Benutzer um.

- Schreibe nichts, was von anderen als Beleidigung aufgefasst werden könnte.
- Vermeide in Konflikte hereingezogen zu werden.
- Hilf mit, dass alle Benutzer, die sich positiv in die Community einzugliedern versuchen, willkommen sind.

**Unter keinen Umständen** akzeptieren wir *beleidigende*, *diskriminierende*, *verletzende*, *gewalttätige*, *sexuell explizite* oder *verleumderische* Inhalte.

### Sei anerkennend!

Erkenne die Leistungen von anderen Benutzern an.

- Vergib einzelne Fehler und sei nicht nachtragend.
- Achte die Arbeit und Mühen von Anderen
- Nimm hilfreiche Hinweise von anderen Benutzern an.

<div class="_alert _alert-danger">
<p><strong>Siehst du einen absichtlichen Verstoß gegen diesen Code of Conduct</strong>, hast du verschiedene Möglichkeiten die Moderatoren, Administratoren und das &pi;-Learn-Team zu kontaktieren, damit diese eingreifen können:</p>
<ol>
<li>Du hast die Möglichkeit, die meisten <em>Inhalte</em> zu <em>melden</em>. Damit tauchen diese auf einer entsprechenden Liste für Moderatoren oder Administratoren auf.</li>
<li>Solltest du einzelne Inhalte nicht melden können. kannst du die entsprechenden <em>Benutzer melden</em>. Diese Möglichkeit findest du auf der Profilseite des Benutzers.</li>
<li>Funktioniert auch dies nicht, kontaktiere das &pi;-Learn-Team über das <a href="/helpdesk"><em>Helpdesk</em></a>.</li>
</ol>
</div>

**Benutzer die gegen diesen Code of Conduct verstoßen, können durch unser Administratoren-Team von der Benutzung der &pi;-Learn Webseite ausgeschlossen werden.**""", "", False, False, False, True, 0, 0],
    [0, True, "default", 1, "data-policy", "legal/data-policy", "Datenschutz", "<p><a href=\"/legal/privacy\">Siehe hier!</a></p>", "", False, False, False, False, 0, 0],
    [0, True, "default", 3, "reputation", "gamification/reputation", "Reputation", """Durch die Bewertung der Inhalte zeigt die Community, wie sehr sie dir vertraut. Daraus errechnet sich eine Punktzahl – deine **Reputation**

Du erhältst Reputation, wenn ...

Ereignis | Betrag
---------|---------
dein Beitrag einen Upvote erhält | +3
ein Benutzer deinem Kurs beitritt | +1
ein Pull Request angenommen wird | max. +50

Dir wird Reputation abgezogen, wenn ...

Ereignis | Betrag
---------|---------
dein Beitrag einen Downvote erhält | -3

Mit steigender Reputation erhältst du Privilegien zur Moderation der Inhalte ...

Reputation | Privileg
-----------|---------
1 |	Beiträge bewerten
100 | Kurse bewerten
1 | Überall kommentieren
1 | Beiträge bearbeiten
100 | Beiträge löschen
200 | Kurse sperren

... und kannst so zusammen mit den Moderierenden zum Erfolg von π-Learn beitragen.""", "", True, False, False, False, 0, 0],
    [0, True, "default", 2, "concept", "concept/konzept-von-pi-learn", "Konzept für π-Learn", "Bei &pi;-Learn kannst du bei verschiedenen Kursen (Workshops) teilnehmen. Daf&uuml;r verdienst du dir Reputationspunkte. Je mehr Punkte du hast, desto mehr Berechtigungen hast du. Zum Beispiel kannst du im Forum Posts als hilfreich markieren oder Kurse bewerten oder dann am Ende auch selber Kurse erstellen oder bearbeiten.", "", False, False, False, False, 0, 0],
    [0, True, "default", 4, "course-hints", "faq/course-hints", "Hinweise zum Umfang und Inhalt eines π-Learn-Kurs", """Falls du dich schon einmal gefragt hast, wie umfangreich ein Kurs auf &pi;-Learn sein soll, bist du hier genau richtig.

## Umfang

Generell kann man sagen, dass für einen &pi;-Learn-Kurs in etwa die selben Rahmengrenzen gelten, wie für einen Forenbeitrag: Er darf nicht **zu spezifisch** sein, so dass er anderen nicht oder nur sehr wenig hilft; wenn das Thema aber ein Buch füllen könnte, ist das Kursthema **zu allgemein**.

Dabei werden bei Kursen natürlich eher allgemeinere Themen behandelt, dass heißt, dass bei Kursen beide Schranken nach oben verschoben werden sollten.

Weiterhin ist ein wichtiges Kriterium, dass ein Kurs, dem Teilnehmer neue Skills/Fähigkeiten/etc. oder interessantes Wissen beibringen kann. Häufig ist dies einer der entscheidenden Faktoren, der einen Kurs nicht zu spezifisch macht.

Da dies relativ abstrakt ist, sind hier ein paar gute und schlechte Beispiele:

- *zu allgemein*: Wie baue ich ein Fahrrad?
- **genau richtig**: Die 5 häufigsten Pannen und wie man diese beheben kann
- *zu spezifisch*: Wie tausche ich die Vorderradlampe Model X von Firma Y gegen die Lampe Model A von Firma B aus?

&nbsp;

- *zu allgemein*: Wie entwickle ich ein eigenes Betriebssystem?
- **genau richtig**: Wie bediene ich den XY-Betriebssystem-Customizer (Baukasten)?
- *zu spezifisch*: Wie behebe ich einen *DRIVER_PAGE_FAULT_ERROR*-Bluescreen?

&nbsp;

- *zu allgemein*: Vollständige Biographien der ägyptischen Königshäuser
- **genau richtig**: Vorstellung von Tut-anch-amun
- *zu spezifisch*: Wie hieß der Nachfolger von Tut-anch-amun?
## Inhalt

Auch wenn ein gutes Kursthema gefunden wurde, muss bei der Erstellung der Inhalte an einige Punkte gedacht werden:

1. Der Kurs sollte zwar nicht zu reißerisch aber doch spannend gestaltet werden. Häufig hilft es Geschichten zu erzählen und unterschiedliche Medien (Text, Bild, Video, Quiz, etc.) abzuwechseln.
2. Es sollte, wenn thematisch möglich, zwischen allen zwei bis drei Inhaltsseiten ein Quiz zur Wiederholung eingefügt werden.
3. Einzelne Inhaltsseiten (Text, Video, ...) sollten einen Bearbeitungsumfang von ca. 20 Minuten nicht überschreiten.""", "", True, False, False, True, 0, 0],
    [0, True, "default", 1, "impress", "legal/impress", "Impressum", "<p>Musst du selber einfügen ;)</p>", "", False, False, False, False, 0, 0],
    [0, True, "default", 4, "markdown", "faq/markdown", "Formatieren von Texten auf π-Learn", """Viele Eingabefelder auf dieser Seite (u.a. Forenbeiträge, Kursvorschläge und Benutzerprofile) unterstützen grundlegende Formatierungen. Dafür wird die Auszeichnungssprache Markdown genutzt. Ein gutes Tutorial findet man [auf der Webseite der CommonMark-Spezifikation](https://commonmark.org/help/tutorial/). Der Übersichtlichkeit halber findest du hier noch einen Überblick über die unterstützten Formatierungen.

## 1. Grundlegende Formatierung

Du kannst in deinem Text Teile **fett** oder *kursiv* markieren und [Hyperlinks](#!) oder ![Bilder](https://img.shields.io/badge/Bilder-ok-brightgreen.svg) hinzufügen. Dafür gilt:

	**fett**
	*kursiv*
	[Hyperlink-Text](/link/ziel)

## 2. Überschriften

Es gibt insgesamt vier unterstützte Ebenen von Überschriften.

<blockquote>
<h1>Erste Ebene</h1>
<h2>Zweite Ebene</h2>
<h3>Dritte Ebene</h3>
<h4>Vierte Ebene</h4>
</blockquote>

Diese werden durch Rautezeichen erstellt:

    # Erste Ebene
    ## Zweite Ebene
    ### Dritte Ebene
    #### Vierte Ebene
		
## 3. Listen

Es ist auch möglich, Listen zu erstellen. Dabei gibt es zwei Arten: geordnete und ungeordnete Listen:

<ol>
	<li>Eine</li>
	<li>Geordnete</li>
	<li>Liste</li>
</ol>
<ul>
	<li>Eine</li>
	<li>Ungeordnete</li>
	<li>Liste</li>
</ul>

	1. Eine
	2. Geordnete
	3. Liste

	- Eine
	- Ungeordnete
	- Liste


## 4. Code & Zitate

Wenn du Programmiercode als solchen deklarieren willst, hast du zwei Möglichkeiten:

1. **Inline**-Code, wenn du nur eine kurze Anweisung, Funktion oder Variable angeben willst: `Code`
	
		Dies ist `Code`

2. **Block**-Code, wenn du einen längeren Abschnitt Code haben willst:
		
			Code wird 4 Leerzeichen eingerückt.
			
Weiterhin kannst du Zitate als solche markieren, indem du jeder Zeile ein `>` voranstellst:

    > Dies ist ein Zitat.
			
## 5. &pi;-Learn-spezifische Besonderheiten.

Es ist möglich auf ein Tag zu verweisen, indem man <code>[&#35;tagname]</code> angibt: [#faq] [#Polynomdivision].

Man kann auch auf Themen verweisen, indem man <code>[&#91;Anzeigetext|URL-Part]]</code> angibt.

## 6. Verwendung von MathJax auf &pi;-Learn

Alle Benutzer haben auf Kursseiten vom Typ "Text" die Möglichkeit, MathJax-Skripte einzubinden.

MathJax-Interpretierung wird mit zwei Doppelpunkten und einer Klammer gestartet <code>::(</code> und beendet <code>)::</code> .""", "", True, True, False, False, 0, 0]
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO help_entry (master_page, active, template, help_cat, url_part, url, title, original_content, override_content, editable_by_admin, subpage_by_admin, is_deprecated, is_pinned, last_change, last_editor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
for help_entry in seeds_help_entry:
    cur.execute(sql, help_entry)

con.commit()
con.close()

print()
print("Seeding help_entry successful.")
print("You'll probably want to change the default.")
print()



print()
print("Seeding modmsg_templates...")
print()

seeds_modmsg_templates = [
    ["Illegitime Bewertungen", """In letzter Zeit haben wir Aktivitäten um dein Konto bemerkt, die durch unseren [Kodex][codex] verboten werden. Diese Aktivitäten betreffen hauptsächlich deine Bewertungen im Forum. Eigentlich darf jeder Benutzer so Beiträge bewerten, wie er es für richtig hält. Diese Freiheit wird nur durch eine Regel eingeschränkt: Bewerte die Inhalte und nicht die Autoren.

Wenn man nämlich Inhalte aufgrund der Autoren bewertet, führt dies dazu dass das ganze Reputations-System nicht mehr funktioniert. Besonders problematisch ist es auch, wenn die Bewertungen eines Kontos gezielt gegen ein anderes Konto gerichtet sind. Dies kann zu unnatürlichen, unfairen Veränderungen der Reputation eines Benutzers führen.

Konkrete Beispiele von solchem Verhalten sind:

- Alle Beiträge eines Benutzers (aus Rache) negativ bewerten.
- Alle Beiträge eines Benutzers positiv bewerten.
- Alle Beiträge eines Bekannten positiv bewerten.
- Beiträge bewerten, damit sich die Reputation des Autors in eine bestimmte Richtung verändert.""", True],
    ["Missbrauch von Zweitkonten", """In letzter Zeit haben wir Aktivitäten um dein Konto bemerkt, die durch unseren [Kodex][codex] verboten werden. Dazu zählt vorallem der Einsatz von mehreren Benutzerkonten, um Aktionen durchzuführen, die dir mir deinem Benutzerkonto alleine nicht möglich wäre. Da solches Verhalten unfair gegenüber anderen Benutzern ist und dem System aktiv schadet, ist es auf &pi;-Learn nicht erlaubt.

Konkrete Beispiele von solchem Verhalten sind:

- Eigene Beiträge bewerten.
- Beiträge mehrfach bewerten.
- Eigene Ideen/Vorschläge unterstützen.
- Umgehen von Blockaden.""", True],
    ["SPAM", """In letzter Zeit haben wir Aktivitäten um dein Konto bemerkt, die durch unseren [Kodex][codex] verboten werden. Hauptsächlich ist uns aufgefallen, dass du häufig über dein Produkt/deine Webseite/deine Arbeit redest, ohne diese beiden Regeln einzuhalten:

1. Erzähle nicht zu viel von deinem Produkt und erzähle nur dann etwas, wenn es zum Thema passt.
2. Wenn du von deinem Produkt erzählst, dann schreibe auch deutlich hin, dass es dein Produkt ist.

Diese beiden Regeln sind dafür da zu sorgen, dass &pi;-Learn für möglichst viele Benutzer nützlich bleibt. Und genau das ist nicht mehr gegeben, wenn die Seite mit Werbung zugemüllt wird.""", True],
    ["Unhöflichkeit", """In letzter Zeit ist uns dein Konto dadurch aufgefallen, dass sich andere Benutzer über dein Verhalten geärgert haben. Wir wollen eine nette Lernatmosphäre für alle schaffen und daher sind beleidigende oder diskriminierende Aussagen auf unserer Webseite fehl am Platz.

Auch wenn es manchmal Momente gibt, in denen man sich ärgert, ist dies dennoch keine Entschuldigung eines oder mehrere dieser oder ähnlicher Sachen zu posten:

- Beleidigungen
- Hänseleien
- Hass-Nachrichten
- Gewaltaufrufe

Wichtig ist außerdem, dass die meisten Handlungen auf dieser Webseite in guter Absicht vorgenommen werden. Darum ist es auch nicht in Ordnung, über Benutzer zu schimpfen, die mithelfen, diese Webseite für alle besser zu machen.""", True],
    ["Umgehen von Beschränkungen", """Dieses Konto existiert nur, um Sperrungen zu umgehen, die entweder vom System oder von einem Moderator gegen ein anderes Konto eingerichtet wurden. In den meisten Fällen sind solche Sperrungen gerechtfertigt und dürfen nicht umgangen werden.

Sollte eine solche Sperrung nicht gerechtfertigt sein, kannst du dem &pi;-Learn-Team dies über den Kontakt-Link im Footer mitteilen. Wir werden diese dann überprüfen und eventuell entsprechende Maßnahmen treffen.

Es ist hingegen nicht erlaubt, neue Konten zu erstellen, um die Sperrung zu umgehen. Solche Konten werden dann entweder die gleiche Sperrung erhalten oder sogar gelöscht. In schweren Fällen kann ein solcher Umgehungsversuch auch dazu führen, dass die Sperrung auf dem ursprünglichen Konto noch verschärft oder verlängert wird.""", True],
    ["Zerstörung eigener Inhalte", """Bitte beachte, dass die Zerstörung eigener Inhalte auf &pi;-Learn nicht erlaubt ist. Mit deiner Registration hast du unseren [Kodex][codex] akzeptiert und uns damit eine unwiderrufliche Veröffentlichungserlaubnis für deine Inhalte unter Creative Commons CC-BY-SA-Lizenz gewährt.

Du kannst allerdings &ndash; nach der CC-BY-SA-Lizenz &ndash; das &pi;-Learn-Team über den Kontakt-Link im Footer informieren, dass du möchtest, dass dein Name von allen oder einzelnen Inhalten von dir entfernt wird.""", True],
    ["Vandalismus", """Alle Inhalte auf dieser Webseite werden unter der Creative Commons CC-BY-SA-Lizenz zur Verfügung gestellt. Dadurch erhält jeder Benutzer die Möglichkeit, diese Inhalte (unter Umständen nach einem Überprüfungs-Prozess) zu bearbeiten. Diese Möglichkeit soll allerdings nur dazu eingesetzt werden, um Beiträge zu verbessern und kleinere Fehler auszubessern.

Es ist nicht erlaubt, Beiträge zu "zerstören". Beispiele dafür sind:

- Werbung zu eigenen Produkten in die Beiträge einfügen.
- Sinnvolle Texte durch Kauderwelsch zu ersetzen. """, True],
    ["Edit-Warring", """Alle Inhalte auf dieser Webseite werden unter der Creative Commons CC-BY-SA-Lizenz zur Verfügung gestellt. Dadurch erhält jeder Benutzer die Möglichkeit, diese Inhalte (unter Umständen nach einem Überprüfungs-Prozess) zu bearbeiten. Natürlich kann es mal vorkommen, dass du der Meinung bist, dass eine solche Bearbeitung fehlerhaft oder schlecht ist. Dann ist es auch in Ordnung, diese zu korrigieren.

Problematisch wird es, wenn der Urheber der Bearbeitung diese Bearbeitung wiederherzustellen versucht. Dies kann dazu führen, dass  beide Benutzer versuchen "ihre" Version des Artikels durchzusetzen.

Solches Verhalten (Edit-Warring) ist auf &pi;-Learn nicht erwünscht.""", True] 
]

con = lite.connect('databases/pilearn.db')
cur = con.cursor()
sql = "INSERT INTO modmsg_templates (title, content, may_be_used) VALUES (?, ?, ?)"
for modmsg_template in seeds_modmsg_templates:
    cur.execute(sql, modmsg_template)

con.commit()
con.close()

print()
print("Seeding modmsg_templates successful.")
print()




print()
print("Seeding user_roles...")
print()


con = lite.connect('databases/pilearn.db')
cur = con.cursor()

cur.execute("""INSERT INTO user_roles (name, is_mod, is_dev, is_team) VALUES ("Normaler Benutzer", 0,0,0), ("Moderator (ernannt)", 1,0,0), ("Moderator (gewählt)", 1,0,0), ("Team (ohne Moderatorenrechte)", 0,0,1), ("Team (mit Moderatorenrechten)", 1,0,1), ("Team (Entwicklerrechte)", 1,1,1)""")

con.commit()
con.close()

print()
print("Seeding user_roles successful.")
print()






print()
print("Seeding badges...")
print()


con = lite.connect('databases/pilearn.db')
cur = con.cursor()

cur.executescript("""
insert into badges (name, class, description, internal_id) values ("Genie", "silver", "Erreiche 100 Reputation", "100-reputation"), ("Hoch und Heilig", "bronze", "Erkläre deine Absicht, an einem Kurs teilzunehmen, der bisher nur als Vorschlag vorliegt.", "first-course-promise"), ("Angebot", "bronze", "Ersten Kursvorschlag eingereicht", "first-course-proposal"), ("Nachfrage", "bronze", "Ersten erfolgreichen Kursvorschlag eingereicht (Kurs wurde erstellt)", "first-course"), ("Unaufhörlich", "silver", "Fünf erfolgreiche Kursvorschläge eingereicht (Kurse wurden erstellt)", "lots-of-courses"), ("Geschafft", "silver", "Ersten Kurs fertiggestellt und veröffentlicht", "first-course-completed"), ("Cooler Kurs", "bronze", "Einen Kurs mit 5 Teilnehmenden anbieten", "course-user-small"), ("Großartiger Kurs", "silver", "Einen Kurs mit 40 Teilnehmenden anbieten", "course-user-medium"), ("Wahnsinniger Kurs", "gold", "Einen Kurs mit 100 Teilnehmenden anbieten", "course-user-large");

insert into badges (name, class, description, internal_id) values ("Anerkennend", "bronze", "Gebe einem Post einen Upvote", "first-upvote"), ("Kritisch", "bronze", "Gebe einem Post einen Downvote", "first-downvote"), ("Stammwähler", "silver", "Gebe 50 Bewertungen von Posts ab.", "lots-of-votes"), ("Cooler Beitrag", "bronze", "Einen Beitrag mit einer Bewertung von 5 veröffentlichen", "post-score-small"), ("Großartiger Beitrag", "silver", "Einen Beitrag mit einer Bewertung von 20 veröffentlichen", "post-score-medium"), ("Wahnsinniger Beitrag", "gold", "Einen Beitrag mit einer Bewertung von 50 veröffentlichen", "post-score-large");


insert into badges (name, class, description, internal_id) values ("Nachgefragt", "bronze", "Poste deine erste Frage (mit positiver Bewertung)", "first-question"), ("Herr Warum", "silver", "Poste fünf Fragen (mit positiver Bewertung)", "lots-of-questions"), ("Erleuchtung", "bronze", "Stelle eine Frage und akzeptiere eine Antwort", "first-accept");

insert into badges (name, class, description, internal_id) values ("Gewusst!", "bronze", "Beantworte eine Frage (mit positiver Bewertung)", "first-answer"), ("Schlaumeier", "silver", "Beantworte fünf Fragen (mit positiver Bewertung)", "lots-of-answers"), ("Besserwisser", "silver", "Drei eigene Antworten wurden akzeptiert, obwohl es weitere Antworten gab.", "better-than-rivalry-answers");

insert into badges (name, class, description, internal_id) values ("Moderator", "gold", "Diene als Community-gewählter Moderator für mindestens ein halbes Jahr (Dieses Abzeichen wird manuell verliehen)", "moderator"), ("Möchtegern-Moderator", "gold", "Nehme als Kandidat an einer Moderatoren-Wahl teil und erreiche die Endrunde", "election-finalist"), ("Wähler", "silver", "Stimme für einen Kandidaten in der Endrunde einer Moderatoren-Wahl", "election-voter")
""")

con.commit()
con.close()

print()
print("Seeding badges successful.")
print()





print()
print("Seeding users...")
print()

print("*********")
print("Configure Admin user:")
admin_email = input("E-Mail: ")
admin_name = input("Display name: ")
admin_pw = input("Password: ")
print("*********")


con = lite.connect('databases/pilearn.db')
cur = con.cursor()

cur.execute("""INSERT INTO user (id, name, realname, email, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, profile_image, last_login, last_email_change, last_password_reset, mergeto, profile_place, profile_website, profile_twitter, profile_projects, member_since, certificate_full_name) VALUES (-1, "System", "System", "", "System-Benutzerkonto", 0, 0, '', 0, 0, 5, 1, '', 0, 0, 0, 0, 'Aleph-1', 'https://www.pilearn.de', '@pi_learn', "", 0, 'Ach du grüne Neune!')""")

cur.execute("""INSERT INTO user (id, name, realname, email, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, profile_image, last_login, last_email_change, last_password_reset, mergeto, profile_place, profile_website, profile_twitter, profile_projects, member_since, certificate_full_name) VALUES (1, ?, ?, ?, '', 0, 0, '', 0, 0, 6, 1, '', 0, 0, 0, 0, '', '', '', '', 0, ?)""", (admin_name, admin_name, admin_email, admin_name))

def sha1(string):
    string = string.encode("utf-8")
    m = hashlib.sha256()
    m.update(string)
    return m.hexdigest()

admin_password = sha1(admin_pw)
cur.execute("INSERT INTO login_methods (user_id, provider, email, password) VALUES (1, 'local_account', ?, ?)", (admin_email, admin_password))

con.commit()
con.close()

print()
print("Seeding users successful.")
print()