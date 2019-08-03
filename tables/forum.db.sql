CREATE TABLE answers (
    id INTEGER PRIMARY KEY,
    forumID INT,
    articleID,
    author INT,
    score INT,
    content TEXT,
    awardRep SMALLINT,
    awardBy INT,
    awardMessage TEXT,
    isAcceptedAnswer TINYINT,

    frozen TINYINT,
    frozenBy INT,
    frozenMessage,

    deleted TINYINT,
    deletionReason VARCHAR(15),

    moderatorNotice TEXT,

    creation_date INT,
    last_edit_date INT,
    last_editor INT
)
;CREATE TABLE answer_revisions (
    id INTEGER PRIMARY KEY,
    forumID INT,
    articleID INT,
    answerID INT,
    editor INT,
    new_content TEXT,
    review_id INT,
    comment VARCHAR(250),
    type VARCHAR(20),
    timestamp INT
)
;CREATE TABLE closure_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT)

;CREATE TABLE closure_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT)

;CREATE TABLE closure_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR(4), reason VARCHAR(20), comment TEXT)

;CREATE TABLE reopen_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT)

;CREATE TABLE reopen_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT)

;CREATE TABLE reopen_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR(4), reason VARCHAR(20), comment TEXT)

;CREATE TABLE article_revisions (
    id INTEGER PRIMARY KEY,
    forumID INT,
    articleID INT,
    new_title VARCHAR(250),
    editor INT,
    new_content TEXT,
    new_tags TEXT,
    review_id INT,
    comment VARCHAR(250)
, type VARCHAR(20),
timestamp INT)

;CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    forumID INT,
    title VARCHAR(150),
    author INT,
    score INT,
    content TEXT,
    tags TEXT,
    awardRep SMALLINT,
    awardBy INT,
    awardMessage TEXT,
    awardStarted INT,
    awardEnded INT,
    hasAcceptedAnswer TINYINT,
    pinned TINYINT,

    frozen TINYINT,
    frozenBy INT,
    frozenMessage TEXT,
    frozenAsLock TINYINT,

    closed TINYINT,
    closureReason VARCHAR(15),
    deleted TINYINT,
    deletionReason VARCHAR(15),

    protected TINYINT,
    protectionBy INT,

    moderatorNotice TEXT,

    creation_date INT,
    last_edit_date INT,
    last_activity_date INT,
    last_editor INT
)

;CREATE TABLE score_votes (id INTEGER PRIMARY KEY, user_id INT, direction TINYINT, reputation TINYINT, target_type VARCHAR(20), target_id INT, nullified TINYINT)

;CREATE TABLE post_deletion_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT)

;CREATE TABLE post_deletion_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT)

;CREATE TABLE post_deletion_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR(4), reason VARCHAR(20), comment TEXT)

;CREATE TABLE post_undeletion_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT)

;CREATE TABLE post_undeletion_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT)

;CREATE TABLE post_undeletion_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR(4), reason VARCHAR(20), comment TEXT)

;CREATE TABLE forum_comments (
  id INTEGER PRIMARY KEY,
  post_type VARCHAR(10),
  post_id INT,
  post_forum INT,
  comment_score INT,
  comment_author INT,
  deleted TINYINT,
  deletedby TINYINT,
  annoyingness TINYINT,
  creation_time INT,
  content TEXT
)

;CREATE TABLE comment_action (
  id INTEGER PRIMARY KEY,
  comment_id INT,
  user_id INT,
  validated TINYINT,
  comment VARCHAR(50),
  action VARCHAR(20)
)
;CREATE TABLE announcements (
  id INTEGER PRIMARY KEY,
  forum INT,
  link VARCHAR(150),
  title VARCHAR(150),
  start_date INT,
  end_date INT,
  show_from INT,
  show_until INT,
  is_featured_banner BOOLEAN
);
CREATE TABLE forum_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forum_id INTEGER NULL,

    name VARCHAR(30),
    excerpt TEXT(300),
    deprecation_notice TEXT(150),

    redirects_to INTEGER,
    applicable BOOLEAN,
    mod_only BOOLEAN
);
INSERT INTO forum_tags (forum_id, name, excerpt, deprecation_notice, redirects_to, applicable, mod_only) VALUES (NULL, "fehler", "Verwende dieses Schlagwort, um Beiträge zu markieren, in denen du auf einen Fehler im Kurs/in der Seite hinweist.", "", 0, 1, 0), (NULL, "support", "Verwende dieses Schlagwort, wenn du fragen willst, wie diese Seite zu bedienen ist.", "", 0, 1, 0), (NULL, "verbesserungsidee", "Verwende dieses Schlagwort, um Beiträge zu markieren, in denen du Ideen vorbringst, wie dieser Kurs/diese Seite verbessert werden könnte.", "", 0, 1, 0), (NULL, "ankündigung", "Verwende dieses Schlagwort für Ankündigungen zum Kurs/zu π-Learn", "", 0, 1, 0), (NULL, "status:erledigt", "Das Problem/Die Idee wurde behoben/umgesetzt.", "", 0, 1, 1), (NULL, "status:in-arbeit", "Das Problem/Die Idee wird behoben/umgesetzt werden; wir arbeiten gerade dran.", "", 0, 1, 1), (NULL, "status:abgelehnt", "Die Idee wird nicht umgesetzt./Es handelt sich nicht um ein Problem sondern um ein absichtlich so entworfenes Feature.", "", 0, 1, 1), (NULL, "faq", "Dieser Beitrag stellt den offizielle *acquis* der Community dar und gilt as Richtlinie für die Webseite.", "", 0, 1, 1);
CREATE TABLE forum_tag_associations (
  post_id INTEGER,
  tag_id INTEGER
);
CREATE TABLE closure_reasons (id INTEGER PRIMARY KEY, name VARCHAR(40), ui_name VARCHAR(40), description TEXT(300), requires_post TINYINT, requires_subreason TINYINT, active TINYINT, not_in_global_forum TINYINT, not_in_course_forum TINYINT, parent INT);
INSERT INTO closure_reasons VALUES
(1, "Duplikat", "bereits gefragt und beantwortet", "Andere hatten dieses Problem auch und fanden bereits eine Antwort", 1, 0, 1, 0, 0, NULL),
(2, "Off Topic", "off-topic", "Dieser Beitrag passt nicht in das ${forum_name}, da ...", 0, 1, 1, 0, 0, NULL),
(3, "Unklar", "unklar", "Es ist nicht klar, was in diesem Beitrag gefragt wird, wie eine Antwort auszusehen hat oder es fehlen kritische Details, die diese Frage nicht beantwortbar machen.", 0, 0, 1, 0, 0, NULL),
(4, "Zu Allgemein", "zu allgemein", "Dieser Beitrag besteht aus mehreren Fragen, hat zu viele mögliche, ununterscheidbar korrekte Antworten oder fordert übertrieben lange Antworten.", 0, 0, 1, 0, 0, NULL),
(5, "Nicht Konstruktiv", "nicht konstruktiv", "Diese Frage kann nur in einer Weise beantwortet werden, die für niemanden wirklich vorteilhaft ist. Es ist nicht möglich, durch eine Antwort auf diese Frage etwas neues zu lernen, außer die Lösung für das spezifische Problem des Fragestellenden", 0, 0, 1, 0, 0, NULL),
(101, "", "off-topic", "Fragen zu Inhalten aus Kursen, Meldungen zu Fehlern in Kursen und Verbesserungsideen zu Kursen gehören nicht in das globale Forum, sondern in das jeweilige Kursforum.", 0, 0, 1, 1, 0, 2),
(102, "", "off-topic", "Support-Fragen, Fehlermeldungen oder Verbesserungsideen zur π-Learn-Software sowie Diskussionen zu Community-Richtlinien gehören nicht in ein Kursforum, sondern in das globale Forum.", 0, 0, 1, 0, 1, 2),
(103, "", "off-topic", "Diese Frage passt nicht in das ${forum_name}, in dem Rahmen, der im Hilfezentrum beschrieben wird.", 0, 0, 0, 0, 1, 2);
CREATE TABLE deletion_votes (
  postType VARCHAR(20),
  postId INT,
  voteOwner INT,
  voteCastDate INT,
  active TINYINT
);

CREATE TABLE post_notices (
  id INTEGER PRIMARY KEY,
  name VARCHAR(50),
  body TEXT(500),
  active TINYINT,
  use_for_lock TINYINT,
  use_for_general TINYINT
);
INSERT INTO post_notices VALUES
(1, "Konflikte über Inhalt", "<p>Dieser Beitrag wurde eingefroren, bis alle Streitigkeiten über den Inhalt beendet sind. Nutze das <a href='/f/0'>globale Forum</a> für alle Diskussionen.</p>", 1, 1, 0),
(2, "Zu viele Kommentare", "<p>Dieser Beitrag wurde eingefroren, da er eine hohe Anzahl an Kommentaren angezogen hat, die entfernt werden mussten. Nutze das <a href='/f/0'>globale Forum</a> für Diskussionen über den Inhalt eines Beitrags.</p>", 1, 1, 0),
(3, "Historische Relevanz", "<p>Dieser Beitrag hat historische Bedeutung aufgrund seines Alters und seiner Verbreitung, stellt aber <strong>kein gutes Beispiel für einen Beitrag in diesem Forum</strong> mehr dar und sollte keinenfalls als Anlass genommen werden, einen ähnlichen Beitrag zu posten.</p><p>Dieser Beitrag und seine Antworten wurden in der Zeit stehen gelassen und können nicht beeinflusst werden.</p>", 1, 1, 0),
(11, "Keine Antwort", "<p>Wir erwarten, dass Antworten bestmöglich versuchen, das konkrete Problem des Fragestellers zu lösen.</p><p><strong>Antworten, bei denen <em>kein Lösungsansatz erkennbar</em> ist, werden gelöscht.</strong></p>", 1, 0, 1),
(12, "Belege erforderlich", "<p>Bitte belege deine Antwort <strong>mit Zitaten, Quellen und anderen, anerkannten und nachvollziehbaren Materialien</strong>.</p><p>Antworten, die nicht hinreichend belegt werden, sind nicht hilfreich für andere Benutzer und können entfernt werden.</p>", 1, 0, 1),
(13, "Aktuelles Ereignis", "<p><strong>Dieser Beitrag betrifft ein aktuelles Ereignis, zu dem sich die Kenntnislage <em>schnell und häufig ändern</em> kann.</strong></p><p>Daher ist es von besonderer Bedeutung, sowohl Verweise zu <em>offizielle Quellen</em> anzugeben, als auch <em>die aktuelle Fassung</em> mit hinreichend genauen Zeitangaben zu zitieren.</p>", 1, 0, 1)
