CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  login_provider VARCHAR(20) NOT NULL,
  verified_email VARCHAR(100) NOT NULL,
  unverified_email VARCHAR(100),
  email_verification_code VARCHAR(50),
  profile_image VARCHAR(100),
  password VARCHAR(100),
  profile_info TEXT,
  profile_link VARCHAR(150),
  profile_place VARCHAR(150),
  profile_personal_name VARCHAR(150),

  role INT NOT NULL,
  reputation INT NOT NULL,

  creation_date DATETIME,
  last_login_date DATETIME,
  last_email_change DATETIME,
  last_password_reset DATETIME,


  banned BOOLEAN,
  ban_reason VARCHAR(30),
  ban_end DATETIME,
)

CREATE TABLE user_roles (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  moderator_powers BOOLEAN,
  developer_powers BOOLEAN
)


CREATE TABLE settings (
  group VARCHAR(50),
  name VARCHAR(50),
  value TEXT
)


CREATE TABLE user_history (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER,
  type INTEGER,
  user_message INTEGER,
  user_message_modified BOOLEAN,
  submission_by INTEGER,
  comment TEXT,
  creation DATETIME
)

CREATE TABLE user_history_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  automatic_id VARCHAR(50),
  manual BOOLEAN
)


CREATE TABLE user_notifications (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER,
  notification_type INTEGER,
  prelink_text VARCHAR(150),
  link_text VARCHAR(150),
  postlink_text VARCHAR(150),
  link_target TEXT
  creation DATETIME,
  seen DATETIME
)

CREATE TABLE user_notification_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  long_name VARCHAR(75),
  description VARCHAR(150),
  short_name VARCHAR(30),
  internal_id VARCHAR(50)
)


CREATE TABLE user_awards (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  award_type INTEGER,
  award_value INTEGER,
  creation DATETIME,
  seen DATETIME
)

CREATE TABLE user_award_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  description VARCHAR(150),
  internal_id VARCHAR(50)
)


CREATE TABLE user_message_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  greetings TEXT,
  body TEXT,
  end_normal TEXT,
  end_suspension TEXT,
  may_be_used BOOLEAN
)

CREATE TABLE badges (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  badge_type INTEGER,
  name VARCHAR(30),
  description TEXT,
  creation DATETIME,
  internal_id VARCHAR(50)
)

CREATE TABLE badge_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(30),
  color VARCHAR(7)
)


CREATE TABLE forum_posts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    forum_id INTEGER,
    post_type INTEGER,

    author INTEGER,
    wiki_status BOOLEAN,
    score INTEGER,
    title VARCHAR(250),
    accept_state TINYINT,
    post_notice INTEGER,

    content TEXT,

    frozen BOOLEAN,
    freeze_by INTEGER,
    freeze_type INTEGER,

    closure DATETIME,
    closure_reason INTEGER,

    deletion DATETIME,
    deletion_reason INTEGER,

    protection DATETIME,
    protection_by INTEGER,

    last_activity DATETIME,
    creation DATETIME
)

CREATE TABLE forum_post_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  internal_id VARCHAR(50)
)


CREATE TABLE forum_post_notices (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  content TEXT,
  for_general BOOLEAN,
  for_lock BOOLEAN,
  for_protection BOOLEAN
)

CREATE TABLE forum_post_freeze_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  applies_to_subposts TINYINT
)

CREATE TABLE forum_post_closure_reasons (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  parent_reason INTEGER,
  name VARCHAR(50),
  excerpt VARCHAR(250),
  content TEXT,
  requires VARCHAR(40),
  applicable BOOLEAN,
  limits VARCHAR(100)
)

CREATE TABLE forum_post_deletion_reasons (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  content TEXT,
  internal_id VARCHAR(50)
)


CREATE TABLE forum_post_revisions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    post_id INTEGER,
    forum_id INTEGER,
    revision_type INTEGER,

    author INTEGER,
    title VARCHAR(250),
    content TEXT,
    tags TEXT,
    post_notice INTEGER,

    closure_reason INTEGER,
    deletion_reason INTEGER,

    creation DATETIME
)

CREATE TABLE forum_post_revision_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  internal_id VARCHAR(50)
)


CREATE TABLE forum_tags (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    forum_id INTEGER NULL,

    name VARCHAR(30),
    excerpt TEXT(300),
    deprecation_notice TEXT(150),

    redirects_to INTEGER,
    applicable BOOLEAN,
    mod_only BOOLEAN,
)

CREATE TABLE forum_tag_associations (
  post_id INTEGER,
  tag_id INTEGER
)


CREATE TABLE forum_votes (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  post_id INTEGER,
  type INTEGER,
  vote_data INTEGER NULL,
  cast DATETIME,
  invalidation DATETIME,
  invalidation_reason INTEGER,
  cast_on_user INTEGER,
  cast_by_user INTEGER
)

CREATE TABLE forum_vote_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  internal_id VARCHAR(50)
)

CREATE TABLE forum_vote_invalidation_reasons (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  internal_id VARCHAR(50),
  allow_recast BOOLEAN,
  allow_recast_after TIME
)

CREATE TABLE forum_comments (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  post_id INTEGER,
  author INTEGER,
  score INTEGER,
  flag_count INTEGER,
  content TEXT,
  creation DATETIME,
  edited BOOLEAN,
  deleted BOOLEAN
)

CREATE TABLE forum_comment_reponses (
  comment_id INTEGER,
  user_id INTEGER,
  response_type INTEGER
)

CREATE TABLE forum_comment_reponse_types (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  internal_id VARCHAR(50)
)
