CREATE TABLE articles (
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


CREATE TABLE score_votes (id INTEGER PRIMARY KEY, user_id INT, direction TINYINT, reputation TINYINT, target_type VARCHAR(20), target_id INT, nullified TINYINT)
