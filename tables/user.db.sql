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

;CREATE TABLE reputation (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR(20), message TEXT, amount INT, recognized TINYINT)

;CREATE TABLE reviewbans (id INTEGER PRIMARY KEY, queue VARCHAR(25), user_id INT, given_by INT, cancelled_by INT, start_date INT, end_date INT, invalidated TINYINT, comment TEXT)

;CREATE TABLE user (
id INTEGER PRIMARY KEY,
name VARCHAR(50),
realname VARCHAR(100),
email VARCHAR(100),
login_provider VARCHAR(20),
password VARCHAR(100),
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
last_password_reset INT
)
;INSERT INTO user (id, name, realname, email, login_provider, password, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, suspension, labels, profile_image, last_login, last_email_change, last_password_reset) VALUES (-2,'system','𝕊𝕐𝕊𝕋𝔼𝕄','','none','','Hallo!\n\nIch führe alle automatisierten Aufgaben durch, die von unserem System erkannt werden.\n\n-----\n\nDein 𝕊𝕐𝕊𝕋𝔼𝕄-Benutzer',0,0,'',0,0,'user',0,'[]','[]','',0,0,0)
;INSERT INTO user (id, name, realname, email, login_provider, password, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, suspension, labels, profile_image, last_login, last_email_change, last_password_reset) VALUES (-1,'admin','𝔸𝔻𝕄𝕀ℕ','','none','','Hallo!\n\nIch führe alle Aufgaben durch, die durch einen Community-Entscheid herbeigeführt wurden, für die also keine einzelnen Benutzer zuständig sind. Weiterhin besitze ich die Community-Beiträge, die jeder bearbeiten kann, der Bearbeitungsvorschläge einreichen kann.\n\n-----\n\nDein 𝔸𝔻𝕄𝕀ℕ-Benutzer',0,0,'',0,0,'user',0,'[]','[]','',0,0,0)
;INSERT INTO user (id, name, realname, email, login_provider, password, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, suspension, labels, profile_image, last_login, last_email_change, last_password_reset) VALUES (1,'paulpidev','paulπdev','maus@paulstrobach.de','local_account','','',0,0,'',0,0,'team.dev',0,'[]','[]','',0,0,0)
;INSERT INTO user (id, name, realname, email, login_provider, password, aboutme, deleted, banned, ban_reason, ban_end, frozen, role, reputation, suspension, labels, profile_image, last_login, last_email_change, last_password_reset) VALUES (2,'9hax','«real9hax»','083329@cryptmail.ddns.net','local_account','','',0,0,'',0,0,'team.dev',0,'[]','[]','',0,0,0)


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
)
