# coding: utf-8
import sqlite3 as lite
import sys
con = None

try:
    con = lite.connect('../databases/pilearn.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE elections (id INTEGER PRIMARY KEY, title VARCHAR(250), message TEXT, places TINYINT, position VARCHAR(50), state TINYINT, minvoterep INT, mincandrep INT)")

    cur.execute("INSERT INTO elections (title, message, places, position, state, minvoterep, mincandrep) VALUES ('Moderatorenwahl 2018', 'Unser Konzept ist es, dass &pi;-Learn eine Community-kontrollierte Open Learning-Plattform sein soll. Dieses Konzept wird zum ersten durch die Reputation erfüllt, eine Punktzahl, die jedem Benutzer aufgrund der Qualität seiner Inhalte zugewiesen wird. Dieser Reputation entsprechen bestimmte Privilegien, mit denen die Benutzer helfen können, diese Seite zu verwalten.\n\nWeiterhin wollen wir, dass jeder sein Wissen gleichberechtigt mit anderen teilen darf und vermeiden es daher, den Inhalt durch von uns beauftragte Benutzer zu moderieren. Statdessen soll dieser Auftrag von den Benutzern dieser Webseite selbst kommen. Darum halten wir bei Bedarf Wahlen ab, um Moderatoren und Administratoren zu ernenen. Diesen Moderatoren und Administratoren kommt eine besondere Verantwortung zu, da sie Zugriff auf die höchsten Privilegien erhalten.\n\nModeratoren verwalten und kontrollieren (\"moderieren\") die Inhalte von π-Learn. Jeder Moderator hat ein bestimmtes Fachgebiet (Thema), für das er verantwortlich ist.\n\nIn dieser Wahl wählen wir einen Moderator für das Thema [[Programmieren|programming]].', 2, 'Moderator', 1, 50, 100)")
    con.commit()

    cur.execute("CREATE TABLE nominations (id INTEGER PRIMARY KEY, election_id INT, message TEXT, answer_score FLOAT, candidate INT, state TINYINT)")

    cur.execute("CREATE TABLE questions (id INTEGER PRIMARY KEY, election_id INT, nomination_id INT, is_community TINYINT, content TEXT, answer TEXT, state TINYINT, asked_date INT, author INT)")

    cur.execute("CREATE TABLE votes (id INTEGER PRIMARY KEY, election_id INT, voter INT, ballot TEXT)")

    #cur.execute("CREATE TABLE nominations (id INTEGER PRIMARY KEY, election_id INT, message TEXT, answer_score FLOAT, candidate INT, state TINYINT)")


    #cur.execute()
    #data = cur.fetchone()
    #data = cur.fetchall()
    #cur.lastrowid

except lite.Error as e:

    print("Error %s:" % e.args)
    sys.exit(1)

finally:
    if con:
        con.close()
