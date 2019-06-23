"""
    cronjob: user_deletion.py
    =========================

    Removes all bindings and profile items for users
    that have been scheduled for deletion.
"""
import sqlite3 as lite

def select_query (
        query_in_table,
        query,
        *data
    ):
    """
        Executes the given :query: in the database file :query_in_table: for the scheduled user :user_id: and yields the result set.
    """

    # Execute :query:
    con = lite.connect('databases/' + query_in_table + '.db')
    cur = con.cursor()
    cur.execute(query, data)

    result = cur.fetchone()
    while result:
        yield result
        result = cur.fetchone()

    con.close()

def execute_query (
        query_in_table,
        query,
        *data
    ):
    """
        Executes the given :query: in the database file :query_in_table: for the scheduled user :user_id:.
    """

    # Execute :query:
    con = lite.connect('databases/' + query_in_table + '.db')
    cur = con.cursor()
    cur.execute(query, data)

    con.commit()
    con.close()

for user in select_query("user","SELECT id,deleted FROM user WHERE deleted != 0 AND Not mergeto AND reputation < 100 LIMIT 10"):
    destroyed = (user[1] == 2)
    user = user[0]
    print "Begin Deleting user",user
    if destroyed:
        print("~ Destroying user (per mod action)")
    print "---"

    execute_query("courses", "UPDATE proposals SET proposer=-3, deleted=1, delete_reason='rule-violation' WHERE proposer=?;", user)

    execute_query("courses","DELETE FROM visits WHERE userid=?;", user)
    execute_query("courses","DELETE FROM commitments WHERE user_id=?;", user)
    execute_query("courses","DELETE FROM enrollments WHERE userid=? AND permission != 4;", user)

    # Do not remove the last course owner without adding -1 (system user)
    for singlecourse in select_query("courses","SELECT courseid, Count(*) AS othercount FROM enrollments WHERE userid=? AND permission = 4 GROUP BY courseid HAVING othercount=1;", user):
        execute_query("courses","INSERT INTO enrollments (courseid, userid, lastunitid, permission) VALUES (?,-1,0,4)", singlecourse[0])

    execute_query("courses","DELETE FROM enrollments WHERE userid=? AND permission = 4;", user)



    if destroyed:
        execute_query("forum","UPDATE answers SET author=-3, deleted=1 WHERE author=?;", user)
    else:
        execute_query("forum","UPDATE answers SET author=-3 WHERE author=?;", user)
    execute_query("forum","UPDATE answers SET frozenBy=-1 WHERE frozenBy=?;", user)

    execute_query("forum","UPDATE answer_revisions SET editor=-3 WHERE editor=?;", user)

    execute_query("forum","UPDATE closure_reviews SET reviewer_id=-1 WHERE reviewer_id=?;", user)
    execute_query("forum","UPDATE closure_flags SET flagger_id=-1, state=-1 WHERE flagger_id=?;", user)


    execute_query("forum","UPDATE reopen_reviews SET reviewer_id=-1 WHERE reviewer_id=?;", user)
    execute_query("forum","UPDATE reopen_flags SET flagger_id=-1, state=-1 WHERE flagger_id=?;", user)


    if destroyed:
        execute_query("forum","UPDATE articles SET author=-3, deleted=1, deletionReason='auto:owner-removed' WHERE author=?;", user)
    else:
        execute_query("forum","UPDATE articles SET author=-3 WHERE author=?;", user)
    execute_query("forum","UPDATE articles SET frozenBy=-1 WHERE frozenBy=?;", user)
    execute_query("forum","UPDATE articles SET protectionBy=-1 WHERE protectionBy=?;", user)

    execute_query("forum","UPDATE article_revisions SET editor=-3 WHERE editor=?;", user)


    execute_query("forum","UPDATE post_deletion_reviews SET reviewer_id=-1 WHERE reviewer_id=?;", user)
    execute_query("forum","UPDATE post_deletion_flags SET flagger_id=-1, state=-1 WHERE flagger_id=?;", user)

    execute_query("forum","UPDATE post_undeletion_reviews SET reviewer_id=-1 WHERE reviewer_id=?;", user)
    execute_query("forum","UPDATE post_undeletion_flags SET flagger_id=-1, state=-1 WHERE flagger_id=?;", user)


    if destroyed:
        execute_query("forum","UPDATE forum_comments SET comment_author=-3, deleted=1, deletedby=-1 WHERE comment_author=?;", user)
    else:
        execute_query("forum","UPDATE forum_comments SET comment_author=-3 WHERE comment_author=?;", user)
    execute_query("forum","UPDATE forum_comments SET deletedby=-1 WHERE deletedby=?;", user)
    execute_query("forum","DELETE FROM comment_action WHERE user_id=?;", user)



    execute_query("election","DELETE FROM nominations WHERE candidate=? AND (SELECT state FROM elections WHERE elections.id=nominations.election_id) != 6;", user)
    if destroyed:
        execute_query("election","DELETE FROM nominations WHERE candidate=?", user)
    else:
        execute_query("election","UPDATE nominations SET candidate=-3 WHERE candidate=?;", user)

    execute_query("election","DELETE FROM questions WHERE author=?;", user)

    execute_query("election","DELETE FROM votes WHERE voter=? AND (SELECT state FROM elections WHERE elections.id=votes.election_id) != 6;", user)
    execute_query("election","UPDATE votes SET voter=-3 WHERE voter=?;", user)


    execute_query("survey","DELETE FROM survey_responses WHERE responder_id=?;", user)
    execute_query("survey","UPDATE surveys SET survey_owner=-3 WHERE survey_owner=?;", user)


    execute_query("helpcenter","UPDATE help_entry SET last_editor=0 WHERE last_editor=?;", user)


    execute_query("user","DELETE FROM notifications WHERE user_id=?;", user)
    execute_query("user","DELETE FROM reputation WHERE user_id=?;", user)
    execute_query("user","DELETE FROM badge_associations WHERE userid=?;", user)

    execute_query("user","DELETE FROM reviewbans WHERE user_id=?;", user)
    execute_query("user","UPDATE reviewbans SET given_by=-1 WHERE given_by=?;", user)

    execute_query("user","UPDATE custom_flag SET flagger_id=-1 WHERE flagger_id=?;", user)


    if destroyed:
        execute_query("user","UPDATE user_uploads SET user_id=-1,removed_by=-1 WHERE user_id=?;", user)
    else:
        execute_query("user","UPDATE user_uploads SET user_id=-1 WHERE user_id=?;", user)

    execute_query("user","DELETE FROM user WHERE id=?;", user)

    print "---"
    print "Completed Deleting user",user
    print ""
    print ""
