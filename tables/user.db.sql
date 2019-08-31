CREATE TABLE enrollments (
course_id INT,
user_id INT,
CONSTRAINT _unique_ UNIQUE (course_id, user_id)
)

;CREATE TABLE notifications (
id INTEGER PRIMARY KEY,
user_id INT,
type VARCHAR(10),
message TEXT,
link VARCHAR(100),
visible TINYINT
)

;CREATE TABLE custom_flaglist (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR(30), state TINYINT, handler INT)

;CREATE TABLE custom_flag (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR(30), queue_id INT, state TINYINT, flagger_id INT, comment TEXT, response TEXT)

;CREATE TABLE annotations (id INTEGER PRIMARY KEY, user_id INT, creator_id INT, creation_date INT, is_hidden TINYINT, content TEXT, type VARCHAR(20))

;CREATE TABLE reputation (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR(20), message TEXT, amount INT, recognized TINYINT, given_date INT)

;CREATE TABLE reviewbans (id INTEGER PRIMARY KEY, queue VARCHAR(25), user_id INT, given_by INT, cancelled_by INT, start_date INT, end_date INT, invalidated TINYINT, comment TEXT)

;CREATE TABLE user (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR(50),
realname VARCHAR(100),
email VARCHAR(100),
aboutme TEXT,
deleted TINYINT,
banned TINYINT,
ban_reason VARCHAR(30),
ban_end INT,
frozen TINYINT,
role VARCHAR(20),
reputation INT,
suspension TEXT,
labels TEXT,
profile_image VARCHAR(100),
last_login INT,
last_email_change INT,
last_password_reset INT,
profile_place VARCHAR(100),
profile_website VARCHAR(150),
profile_twitter VARCHAR(150),
profile_projects TEXT,
member_since INT,
certificate_full_name VARCHAR(150)
)
;CREATE TABLE login_methods (
  id INTEGER PRIMARY KEY,
  user_id INT,
  provider VARCHAR(20),
  email VARCHAR(100),
  password VARCHAR(100),
  last_used INT,
  last_verified INT
)

;INSERT INTO user (id, name, realname, email, login_provider, password, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, suspension, labels, profile_image, last_login, last_email_change, last_password_reset) VALUES (-1,'System','System','','none','','Hallo Welt!',0,0,'',0,0,2,0,'[]','[]','',0,0,0)


;CREATE TABLE role_table (
id INTEGER PRIMARY KEY,
user_id INT,
role VARCHAR(30),
scope_comment VARCHAR(200),
active TINYINT,
shown TINYINT,
appointment_date INT,
election_link VARCHAR(100),
resignation_date INT,
comment TEXT
);
CREATE TABLE user_uploads (
  id INTEGER PRIMARY KEY,
  user_id INT,
  file_path VARCHAR(50),
  removed_by INT,
  upload_at INT,
  file_size INT
);
create table modmsg_threads (
  id INTEGER PRIMARY KEY,
  initiated_by INT,
  last_activity INT,
  contacted_user INT,
  closed TINYINT
);
create table modmsg_messages (
  id INTEGER PRIMARY KEY,
  thread_id INT,
  submitted_by INT,
  submission_time INT,
  message_receiver INT,
  content TEXT,
  suspension_length INT,
  template INT,
  closed_thread TINYINT
);
create table modmsg_templates (
  id INTEGER PRIMARY KEY,
  title VARCHAR(50),
  content TEXT,
  may_be_used TINYINT
);

create table badges (id INTEGER PRIMARY KEY, name VARCHAR(40), class VARCHAR(10), description TEXT, internal_id VARCHAR(50));create table badge_associations (userid INT, badgeid INT, data TEXT, recognized TINYINT, given_date INT);

insert into badges (name, class, description, internal_id) values ("Genie", "silver", "Erreiche 100 Reputation", "100-reputation"), ("Hoch und Heilig", "bronze", "Erkläre deine Absicht, an einem Kurs teilzunehmen, der bisher nur als Vorschlag vorliegt.", "first-course-promise"), ("Angebot", "bronze", "Ersten Kursvorschlag eingereicht", "first-course-proposal"), ("Nachfrage", "bronze", "Ersten erfolgreichen Kursvorschlag eingereicht (Kurs wurde erstellt)", "first-course"), ("Unaufhörlich", "silver", "Fünf erfolgreiche Kursvorschläge eingereicht (Kurse wurden erstellt)", "lots-of-courses"), ("Geschafft", "silver", "Ersten Kurs fertiggestellt und veröffentlicht", "first-course-completed"), ("Cooler Kurs", "bronze", "Einen Kurs mit 5 Teilnehmenden anbieten", "course-user-small"), ("Großartiger Kurs", "silver", "Einen Kurs mit 40 Teilnehmenden anbieten", "course-user-medium"), ("Wahnsinniger Kurs", "gold", "Einen Kurs mit 100 Teilnehmenden anbieten", "course-user-large");

insert into badges (name, class, description, internal_id) values ("Anerkennend", "bronze", "Gebe einem Post einen Upvote", "first-upvote"), ("Kritisch", "bronze", "Gebe einem Post einen Downvote", "first-downvote"), ("Stammwähler", "silver", "Gebe 50 Bewertungen von Posts ab.", "lots-of-votes"), ("Cooler Beitrag", "bronze", "Einen Beitrag mit einer Bewertung von 5 veröffentlichen", "post-score-small"), ("Großartiger Beitrag", "silver", "Einen Beitrag mit einer Bewertung von 20 veröffentlichen", "post-score-medium"), ("Wahnsinniger Beitrag", "gold", "Einen Beitrag mit einer Bewertung von 50 veröffentlichen", "post-score-large");


insert into badges (name, class, description, internal_id) values ("Nachgefragt", "bronze", "Poste deine erste Frage (mit positiver Bewertung)", "first-question"), ("Herr Warum", "silver", "Poste fünf Fragen (mit positiver Bewertung)", "lots-of-questions"), ("Erleuchtung", "bronze", "Stelle eine Frage und akzeptiere eine Antwort", "first-accept");

insert into badges (name, class, description, internal_id) values ("Gewusst!", "bronze", "Beantworte eine Frage (mit positiver Bewertung)", "first-answer"), ("Schlaumeier", "silver", "Beantworte fünf Fragen (mit positiver Bewertung)", "lots-of-answers"), ("Besserwisser", "silver", "Drei eigene Antworten wurden akzeptiert, obwohl es weitere Antworten gab.", "better-than-rivalry-answers");

insert into badges (name, class, description, internal_id) values ("Moderator", "gold", "Diene als Community-gewählter Moderator für mindestens ein halbes Jahr (Dieses Abzeichen wird manuell verliehen)", "moderator"), ("Möchtegern-Moderator", "gold", "Nehme als Kandidat an einer Moderatoren-Wahl teil und erreiche die Endrunde", "election-finalist"), ("Wähler", "silver", "Stimme für einen Kandidaten in der Endrunde einer Moderatoren-Wahl", "election-voter")

insert into badges (name, class, description, internal_id) values ("Beta", "gold", "Sei aktiv während der Beta von π-Learn und erhalte mindestens 10 Reputation", "beta"), ("Skimaske", "gold", "Finde eine Sicherheitslücke auf π-Learn und melde sie zuerst an das π-Learn-Team, um so für die Sicherheit der Webseite zu sorgen (Dieses Abzeichen wird manuell verliehen)", "hacker")

;CREATE TABLE user_roles (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50),
  is_mod TINYINT,
  is_dev TINYINT,
  is_team TINYINT
);
INSERT INTO user_roles (name, is_mod, is_dev, is_team) VALUES ("Normaler Benutzer", 0,0,0), ("Moderator (ernannt)", 1,0,0), ("Moderator (gewählt)", 1,0,0), ("Team (ohne Moderatorenrechte)", 0,0,1), ("Team (mit Moderatorenrechten)", 1,0,1), ("Team (Entwicklerrechte)", 1,1,1)
;CREATE TABLE user_preference_overrides (
  user_id INT,
  pref_key VARCHAR(50),
  value TEXT
)
;CREATE TABLE password_reset_requests (
  id INTEGER PRIMARY KEY,
  user_id INT,
  login_method_id INT,
  creation_date INT,
  deletion_date INT,
  verification_code VARCHAR(7)
)
