# coding: utf-8
import sqlite3 as lite
import sys
con = None

try:
    con = lite.connect('../databases/helpdesk.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE tickets (id INTEGER PRIMARY KEY, title VARCHAR(250), department VARCHAR(50), closed TINYINT, repro TINYINT, deferred TINYINT, assoc INT, type VARCHAR(20), last_response_id INT)")

    cur.execute("CREATE TABLE responses (id INTEGER PRIMARY KEY, ticket_id INT, message TEXT, poster INT, official TINYINT)")

    cur.execute("CREATE TABLE viewrights (id INTEGER PRIMARY KEY, ticket_id INT, person INT)")

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
