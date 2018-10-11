# coding: utf-8
import sqlite3 as lite
import sys

con = None

try:
    con = lite.connect('chat.db')

    cur = con.cursor()
    cur.execute("""
    CREATE TABLE rooms (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        description TEXT,
        frozen TINYINT,
        suspended TINYINT,
        suspension_end INT,
        public_read TINYINT,
        public_write TINYINT
    )
    """)

    cur.execute(u"""
    INSERT INTO rooms (id, name, description, frozen, suspended, suspension_end, public_read, public_write) VALUES (1, 'Fragen an die Entwickler', 'Stellen Sie hier Fragen an die Entwickler von π-Learn', 0, 0, 0, 1, 1)
    """)

    cur.execute(u"""
    INSERT INTO rooms (id, name, description, frozen, suspended, suspension_end, public_read, public_write) VALUES (2, 'Support', 'Support für die π-Learn-Seite', 0, 0, 0, 1, 1)
    """)

    cur.execute("""
    CREATE TABLE user (
        id INTEGER PRIMARY KEY,
        assoc_id INT,
        name VARCHAR(50),
        may_talk TINYINT,
        is_mod TINYINT,
        is_suspended TINYINT,
        suspension_reason TINYINT,
        suspension_end INT
    )
    """)

    cur.execute(u"""
    INSERT INTO user (id, assoc_id, name, may_talk, is_mod, is_suspended, suspension_reason, suspension_end) VALUES (1, 1, 'paulπdev', 1, 1, 0, '', 0)
    """)

    cur.execute(u"""
    INSERT INTO user (id, assoc_id, name, may_talk, is_mod, is_suspended, suspension_reason, suspension_end) VALUES (2, 2, '9hax', 1, 0, 0, '', 0)
    """)

    cur.execute("""
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY,
        room_id INT,
        poster_id INT,
        reply_id INT,
        is_shown TINYINT,
        content TEXT,
        is_mod TINYINT,
        was_edited TINYINT,
        send_at INT
    )
    """)

    cur.execute("""
    CREATE TABLE message_events (
        id INTEGER PRIMARY KEY,
        room_id INT,
        event VARCHAR(30),
        message_id INT,
        content TEXT,
        triggered_at INT
    )
    """)

    cur.execute("""
    CREATE TABLE message_flags (
        id INTEGER PRIMARY KEY,
        room_id INT,
        flagger INT,
        message_id INT,
        is_handled TINYINT,
        outcome TINYINT,
        message TEXT
    )
    """)

except lite.Error as e:

    print("Error %s:" % e.args)
    sys.exit(1)

finally:

    if con:
        con.close()
