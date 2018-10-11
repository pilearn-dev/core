CREATE TABLE elections (id INTEGER PRIMARY KEY, title VARCHAR(250), message TEXT, places TINYINT, position VARCHAR(50), state TINYINT, minvoterep INT, mincandrep INT)

;CREATE TABLE nominations (id INTEGER PRIMARY KEY, election_id INT, message TEXT, answer_score FLOAT, candidate INT, state TINYINT)

;CREATE TABLE questions (id INTEGER PRIMARY KEY, election_id INT, nomination_id INT, is_community TINYINT, content TEXT, answer TEXT, state TINYINT, asked_date INT, author INT)

;CREATE TABLE votes (id INTEGER PRIMARY KEY, election_id INT, voter INT, ballot TEXT)
