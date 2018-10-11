# coding: utf-8
import sqlite3 as lite
import sys
from sha1 import sha1

con = None

try:
    con_courses = lite.connect('databases/courses.db')
    con_user = lite.connect('databases/user.db')
    con_forum = lite.connect('databases/forum.db')

    cur = con_courses.cursor()
    cur.execute("""
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        title VARCHAR(150),
        shortdesc TEXT(200),
        longdesc TEXT,
        materials TEXT,
        state TINYINT,
        getcert TINYINT,
        highqual TINYINT,
        admincourse TINYINT
    )
    """)
    cur.execute("""
    CREATE TABLE lessons (
        id INTEGER PRIMARY KEY,
        course_id INT
        title VARCHAR(150),
        order_ INT,
        type VARCHAR(15),
        content TEXT,
        state TINYINT
    )
    """)
    cur.execute("""
    INSERT INTO courses (title, shortdesc, longdesc, materials, state, getcert, highqual, admincourse) VALUES (
        'Beispiel-Kurs',
        'Dies ist ein Beispielkurs',
        'Dieser Kurs bringt keine Inhalte auf diese Webseite, sondern dient allein dem Testen des Systems.',
        'Du musst ein Administrator sein, um diesen Kurs nutzen zu dürfen.',
        2,
        0,
        0,
        1
    )
    """)
    con_courses.commit()
    cur.execute("""
    CREATE TABLE course_proposals (
        id INTEGER PRIMARY KEY,
        title VARCHAR(150),
        shortdesc TEXT(200),
        longdesc TEXT,
        materials TEXT,
        state TINYINT,
        score TINYINT,
        author INT,
        actor INT
    )
    """)
    cur.execute("""
    CREATE TABLE proposal_votes (
        prop_id INT,
        user_id INT,
        vote TINYINT
    )
    """)
    cur.execute("""
    CREATE TABLE authorship (
        course_id INT,
        user_id INT,

        CONSTRAINT _unique_ UNIQUE (course_id, user_id)
    )
    """)
    cur = con_user.cursor()
    cur.execute("""
    CREATE TABLE user (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        realname VARCHAR(100),
        email  VARCHAR(100),
        password VARCHAR(100),
        aboutme TEXT,
        state TINYINT,
        frozen TINYINT,
        role VARCHAR(1),
        reputation INT,
        suspension TEXT
    )
    """)
    cur.execute("CREATE TABLE reputation (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR(20), message TEXT, amount INT)")
    cur.execute("""
    CREATE TABLE user_flags (
        id INTEGER PRIMARY KEY,
        user_id INT,
        flagtype VARCHAR(4),
        flagreason VARCHAR(10),
        flagmessage TEXT,
        bywho INT,
        active TINYINT,
        handledby INT,
        handlereason TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE enrollments (
        course_id INT,
        user_id INT,

        CONSTRAINT _unique_ UNIQUE (course_id, user_id)
    )
    """)
    cur.execute(u"""
    INSERT INTO user (id, name, realname, email, password, state, role, reputation, aboutme) VALUES (
        -2,
        'system',
        '𝕊𝕐𝕊𝕋𝔼𝕄',
        '',
        '',
        -1,
        'a',
        1,
        'Hallo!\n\nIch führe alle automatisierten Aufgaben durch, die von unserem System erkannt werden.\n\n-----\n\nDein 𝕊𝕐𝕊𝕋𝔼𝕄-Benutzer'
    )
    """)
    con_user.commit()
    cur.execute(u"""
    INSERT INTO user (id, name, realname, email, password, state, role, reputation, aboutme) VALUES (
        -1,
        'admin',
        '𝔸𝔻𝕄𝕀ℕ',
        '',
        '',
        -1,
        'a',
        1,
        'Hallo!\n\nIch führe alle Aufgaben durch, die durch einen Community-Entscheid herbeigeführt wurden, für die also keine einzelnen Benutzer zuständig sind. Weiterhin bin ich Herausgeber aller Wahl-Posts im globalen Forum und besitze die anonymen Beiträge.\n\n-----\n\nDein 𝔸𝔻𝕄𝕀ℕ-Benutzer'
    )
    """)
    con_user.commit()
    cur.execute(u"""
    INSERT INTO user (id, name, realname, email, password, state, role, reputation, aboutme) VALUES (
        1,
        'paulpidev',
        'paulpidev',
        'maus@paulstrobach.de',
        '"""+sha1("@zugang@")+"""',
        1,
        'd',
        1,
        ?
    )
    """, (u"Hallo, mein Name ist Paul.  \nIch bin Entwickler und Erfinder von π-Learn. Diese Webseite habe ich mit `Python`, `Javascript`, `SQL`, `CSS` und `HTML` programmiert. Ich kann aber auch noch `PHP`, etwas Java sowie ein wenig `C#` und `C++`.\n\n> Wenn ihr mehr über mich und π-Learn erfahren wollt, könnt ihr meinen  [Blog][1] besuchen.\n\n\n[1]: /forum/0/global/article/1/pauls-blog\n\n-----\n\nPaul", ))
    con_user.commit()
    cur.execute("""
    CREATE TABLE notifications (
        id INTEGER PRIMARY KEY,
        user_id INT,
        type VARCHAR(10),
        message TEXT,
        link VARCHAR(100),
        visible TINYINT
    )
    """)

    # NEW:
    cur = con_forum.cursor()
    cur.execute("""
    CREATE TABLE fo_articles (
        id INTEGER PRIMARY KEY,
        forum_id INT,
        title VARCHAR(250),
        state TINYINT,
        award SMALLINT,
        accepted_answer TINYINT,
        locked TINYINT,
        pinned TINYINT,
        election TINYINT,
        author INT,
        score INT,
        content TEXT,
        tags TEXT,
        closeReason VARCHAR(20),
        closeMessage TEXT,
        lockMessage TEXT,
        modMessage TEXT,
        deleteReason VARCHAR(100)
    )
    """)
    cur.execute("CREATE TABLE fo_votes (id INTEGER PRIMARY KEY, user_id INT, type VARCHAR(10), subtype VARCHAR(20), message TEXT, whatfor VARCHAR(3), target_id INT)")
    cur.execute("CREATE TABLE fo_answers (id INTEGER PRIMARY KEY, forum_id INT, article_id INT, state TINYINT, award SMALLINT, is_accepted TINYINT, author INT, score INT, content TEXT, modMessage TEXT, deleteReason VARCHAR(100))");

    #cur.execute()
    #data = cur.fetchone()
    #data = cur.fetchall()
    #cur.lastrowid

except lite.Error as e:

    print("Error %s:" % e.args)
    sys.exit(1)

finally:

    if con_courses:
        con_courses.close()
    if con_user:
        con_user.close()
    if con_forum:
        con_forum.close()
