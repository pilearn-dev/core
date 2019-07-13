CREATE TABLE courses (
    id integer PRIMARY KEY AUTOINCREMENT,
    topicid integer,
    title varchar,
    shortdesc varchar,
    longdesc text,
    requirements text,
    byline varchar,
    sponsorid integer,
    state integer
)

;CREATE TABLE enrollments (
    id integer PRIMARY KEY AUTOINCREMENT,
    courseid integer,
    userid integer,
    lastunitid integer,
    permission tinyint
)

;CREATE TABLE units (
    id integer PRIMARY KEY AUTOINCREMENT,
    title varchar,
    courseid integer,
    content text,
    type varchar,
    parent integer,
    availible integer
    unit_order integer
)

;CREATE TABLE visits (
    id integer PRIMARY KEY AUTOINCREMENT,
    courseid integer,
    userid integer,
    unitid integer,
    data text
)

;CREATE TABLE topics (
	id integer PRIMARY KEY AUTOINCREMENT,
	name varchar,
	title varchar,
	excerpt varchar,
	description text,
	giveable integer
)

;CREATE TABLE proposals (
    id integer PRIMARY KEY AUTOINCREMENT,
    topicid integer,
    title varchar,
    shortdesc varchar,
    longdesc text,
    requirements text,
    proposer integer,
    score integer,
    declined integer,
    decline_reason text,
    deleted integer,
    delete_reason text,
    courseid integer,
    proposal_time INT
)

;CREATE TABLE commitments (
    id INTEGER PRIMARY KEY,
    proposal_id INT,
    course_id INT,
    user_id INT,
    worth FLOAT,
    fulfilled TINYINT,
    creation_time INT,
    activation_time INT,
    invalidated TINYINT
)
;create table branches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author INT,
  course_id INT,
  pull_request INT NULL,
  abandoned BOOLEAN,
  abandoned_date INT,
  decision TINYINT,
  decision_date INT,
  hide_as_spam BOOLEAN,
  delta_factor SMALLINT
)
;create table pull_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author INT,
  branch_id INT,
  course_id INT,
  title VARCHAR(150),
  description TEXT (1050),
  proposal_date INT,
  decision TINYINT,
  decision_date INT,
  hide_as_spam BOOLEAN
)
;create table branch_overrides (
  id INTEGER PRIMARY KEY,
  branch INT,
  overrides INT NULL,
  parent_unit INT NULL,
  parent_override INT NULL,
  title VARCHAR(150),
  content TEXT,
  type VARCHAR(25),
  unit_order INT,
  changed BOOLEAN,
  created BOOLEAN
)
