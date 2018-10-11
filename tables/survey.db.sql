CREATE TABLE survey_responses (
id INTEGER PRIMARY KEY,
survey_id INT,
responder_id INT,
content TEXT
)
;CREATE TABLE surveys (
id INTEGER PRIMARY KEY,
title VARCHAR(100),
content TEXT,
results TEXT,
state TINYINT,
associated_forum INT,
survey_owner INT
)
