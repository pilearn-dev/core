"""
    migration: migrate_login_data.py
    ================================

    Migrate login data by moving them to external table
"""
import sqlite3 as lite

con = lite.connect('databases/user.db')

def select_query (
        query_in_table,
        query,
        *data
    ):
    """
        Executes the given :query: in the database file :query_in_table: for the given :data: and yields the result set.
    """
    global con

    # Execute :query:
    cur = con.cursor()
    cur.execute(query, data)

    result = cur.fetchone()
    while result:
        yield result
        result = cur.fetchone()

def execute_query (
        query_in_table,
        query,
        *data
    ):
    """
        Executes the given :query: in the database file :query_in_table: for the given :data:.
    """
    global con

    # Execute :query:
    cur = con.cursor()
    cur.execute(query, data)

    con.commit()

for user in select_query("user","SELECT id, login_provider, email, password FROM user WHERE id >= 1"):

    id, login_provider, email, password = user

    if login_provider == "oauth:google":
        password = None

    execute_query("user", "INSERT INTO login_methods (user_id, provider, email, password) VALUES (?, ?, ?, ?)", id, login_provider, email, password)


con.close()
