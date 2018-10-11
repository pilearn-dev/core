CREATE TABLE responses (id INTEGER PRIMARY KEY, ticket_id INT, message TEXT, poster INT, official TINYINT)

;CREATE TABLE tickets (id INTEGER PRIMARY KEY, title VARCHAR(250), department VARCHAR(50), closed TINYINT, repro TINYINT, deferred TINYINT, assoc INT, type VARCHAR(20), last_response_id INT)

;CREATE TABLE viewrights (id INTEGER PRIMARY KEY, ticket_id INT, person INT)
