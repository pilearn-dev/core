# coding: utf-8
import sqlite3 as lite
import sys

con = None

try:
    #con = lite.connect('databases/forum.db')
    con = lite.connect('../databases/user.db')

    cur = con.cursor()
    con.executescript("""UPDATE user SET banned=0, deleted=0;
    """)
    con.commit()

except lite.Error as e:

    print("Error %s:" % e.args)
    sys.exit(1)

finally:

    if con:
        con.close()
