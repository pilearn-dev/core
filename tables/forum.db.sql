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

    moderatorNotice TEXT
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
    type VARCHAR(20)
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

    moderatorNotice TEXT
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
