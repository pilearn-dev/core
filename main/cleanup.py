import sqlite3 as lite

con = None

# Cleanup-script #1: ResetMyAccount
try:
    con = lite.connect('../databases/user.db')
    cur = con.cursor()
    cur.execute("""
    UPDATE user SET state='1', role='d' WHERE id='1';
    """)
    con.commit()
except SyntaxError as e:
    print("Error %s:" % e.args)
finally:
    if con:
        con.close()

# Cleanup-script #1: DestroyNominatedPosts
try:
    con = lite.connect('../databases/forum.db')
    cur = con.cursor()
    cur.execute("""
    DELETE FROM articles WHERE deleted=2;
    """)
    cur.execute("""
    DELETE FROM answers WHERE deleted=2;
    """)
    con.commit()
except SyntaxError as e:
    print("Error %s:" % e.args)
finally:
    if con:
        con.close()

# END OF FILE
